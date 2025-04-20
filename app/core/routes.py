"""
Routes for the QA System
"""

import os
import logging
import google.generativeai as genai
from flask import Blueprint, render_template, request, jsonify, current_app
from PIL import Image
import uuid
from werkzeug.utils import secure_filename

from app.utils.file_handler import handle_uploaded_file, allowed_file
from app.services.file_processor import process_file, is_url, is_youtube_url, text_to_vector
from app.services.youtube_service import summarize_youtube_video
from app.services.vector_service import store_in_vector_db, find_similar_content, store_qa_pair
from app.services.langsmith_monitor import get_langsmith_monitor

# Set up logging
logger = logging.getLogger(__name__)

# Initialize models
text_model = genai.GenerativeModel('gemini-1.5-pro')
vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Using the recommended model

# Initialize LangSmith monitor
langsmith_monitor = get_langsmith_monitor()

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/chat', methods=['POST'])
def chat():
    try:
        # Initialize response
        response_data = {
            'answer': '',
            'error': None,
            'similar_content': []
        }

        # Get message from request - handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '')
            logger.info(f"Received JSON request with message: {message[:50]}...")
        else:
            message = request.form.get('message', '')
            logger.info(f"Received form request with message: {message[:50]}...")

        # Check if the message is a URL
        is_message_url = is_url(message)
        file_info = None

        # Process URL in message if it's a URL
        if is_message_url:
            logger.info(f"Message contains URL: {message}")

            # Check if it's a YouTube URL
            if is_youtube_url(message):
                logger.info(f"Processing YouTube URL: {message}")

                # Process the YouTube URL
                file_info = process_file(message)

                # Check if we have any information
                if file_info and file_info['file_type'] == 'youtube':
                    # Generate a summary even if there are errors
                    summary = summarize_youtube_video(message, file_info['text'] or "Unable to retrieve video information")

                    # Store in vector database if available and we have a vector
                    if file_info.get('vector') is not None:
                        metadata = {
                            'type': 'youtube',
                            'url': message,
                            'summary': summary[:500]  # Store a snippet of the summary
                        }
                        doc_id = store_in_vector_db(file_info['text'], file_info['vector'], metadata)
                        if doc_id:
                            logger.info(f"Stored YouTube transcript in AstraDB with ID: {doc_id}")

                    # Set the response
                    response_data['answer'] = summary
                    return jsonify(response_data)
                else:
                    # Handle case where file_info is None or not a YouTube type
                    error_msg = "Unable to process YouTube URL. Please check the URL and try again."
                    logger.error(error_msg)
                    response_data['error'] = error_msg
                    return jsonify(response_data), 400
            else:
                # Not a YouTube URL, process normally
                file_info = process_file(message)

        # Check if there's a file in the request
        file_path = None

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            logger.info(f"Received file: {file.filename}")

            # Save and process the file
            file_path, error = handle_uploaded_file(file)
            if error:
                return jsonify({'error': error}), 400

            # Process the file to extract text and generate vector representation
            file_info = process_file(file_path)
            logger.info(f"File type: {file_info['file_type']}")

            if file_info['error']:
                return jsonify({'error': f"Failed to process the file: {file_info['error']}"}), 400

        # Find similar content based on the message or file vector
        similar_content = []
        message_vector = None

        # Get vector from message if available
        if message and message.strip():
            message_vector = text_to_vector(message)

        # Use file vector if available, otherwise use message vector
        search_vector = file_info['vector'] if file_info and file_info['vector'] is not None else message_vector

        if search_vector is not None:
            # Search for similar content including Q&A pairs
            similar_docs = find_similar_content(search_vector, limit=5)

            # Process and categorize results
            qa_pairs = []
            other_docs = []

            for doc in similar_docs:
                if '_id' in doc and 'text' in doc:
                    # Check if it's a Q&A pair
                    if doc.get('type') == 'qa_pair' or ('question' in doc and 'answer' in doc):
                        qa_pairs.append(doc)
                    else:
                        other_docs.append(doc)

            # Log what we found
            if qa_pairs:
                logger.info(f"Found {len(qa_pairs)} similar Q&A pairs")
            if other_docs:
                logger.info(f"Found {len(other_docs)} similar documents")

            # Process for display in UI
            for doc in similar_docs:
                if '_id' in doc and 'text' in doc:
                    # Only include a snippet of the text to avoid large responses
                    text_snippet = doc['text'][:500] + "..." if len(doc['text']) > 500 else doc['text']
                    similar_content.append({
                        'id': doc['_id'],
                        'text': text_snippet,
                        'type': doc.get('type', 'unknown'),
                        'url': doc.get('url', None),
                        'similarity': doc.get('$similarity', 0),
                        'is_qa_pair': doc.get('type') == 'qa_pair' or ('question' in doc and 'answer' in doc)
                    })

            # Add to response data
            response_data['similar_content'] = similar_content

            # Enhance the prompt with context from similar content
            if similar_docs:
                context_parts = []

                # Add Q&A pairs first if available
                if qa_pairs:
                    qa_context = "\n\n".join([f"Q: {doc.get('question', '')}\nA: {doc.get('answer', '')}"
                                           for doc in qa_pairs])
                    context_parts.append(f"Similar questions and answers:\n{qa_context}")

                # Add other document content
                if other_docs:
                    doc_context = "\n\n".join([doc.get('text', '')[:500] for doc in other_docs])
                    context_parts.append(f"Context from similar documents:\n{doc_context}")

                # Combine all context
                if context_parts:
                    context = "\n\n".join(context_parts)

                    # Enhance the message with context
                    if message:
                        message = f"{message}\n\n{context}"
                    else:
                        message = f"Please analyze this content:\n\n{context}"

        # Generate content based on message and file
        if file_info and file_info['file_type'] == 'image':
            # For images, use the vision model
            image = Image.open(file_path)
            logger.info(f"Using vision model: {vision_model._model_name}")

            # Create a unique run ID for tracing
            run_id = str(uuid.uuid4())

            # Wrap the model call with LangSmith monitoring
            @langsmith_monitor.trace(run_type="llm", name="vision_model_generate", tags=["vision", "image_analysis"])
            def generate_vision_content(prompt, img):
                if prompt:
                    logger.info(f"Generating content with message and image")
                    return vision_model.generate_content([prompt, img])
                else:
                    logger.info(f"Generating content with image only")
                    return vision_model.generate_content(img)

            # Call the wrapped function
            response = generate_vision_content(message, image)

            response_data['answer'] = response.text
        elif file_info and file_info['text']:
            # For text-based files, include the extracted content in the prompt
            file_type = file_info['file_type'].upper()
            extracted_text = file_info['text']

            # Create a prompt that includes the file content
            combined_prompt = f"{message}\n\nContent extracted from {file_type} file:\n{extracted_text}"
            logger.info(f"Using text model with extracted content from {file_type}")

            # Wrap the model call with LangSmith monitoring
            @langsmith_monitor.trace(run_type="llm", name="text_model_with_file", tags=["text", file_type.lower()])
            def generate_text_content_with_file(prompt):
                return text_model.generate_content(prompt)

            # Call the wrapped function
            response = generate_text_content_with_file(combined_prompt)
            response_data['answer'] = response.text

            # Store in vector database if available
            if file_info['vector'] is not None:
                # Store the document content
                metadata = {
                    'type': file_info['file_type'],
                    'query': message,
                    'answer': response_data['answer'][:500]  # Store a snippet of the answer
                }
                doc_id = store_in_vector_db(extracted_text, file_info['vector'], metadata)
                if doc_id:
                    logger.info(f"Stored {file_type} content in AstraDB with ID: {doc_id}")

                # Also store the Q&A pair
                qa_vector = text_to_vector(message + " " + response_data['answer'])
                qa_metadata = {
                    'source_type': file_info['file_type'],
                    'source_id': doc_id
                }
                qa_id = store_qa_pair(message, response_data['answer'], qa_vector, qa_metadata)
                if qa_id:
                    logger.info(f"Stored Q&A pair in AstraDB with ID: {qa_id}")
        else:
            # Text-only query
            if not message.strip():
                return jsonify({'error': 'No message provided'}), 400

            logger.info(f"Using text model for message: {message[:50]}...")

            # Wrap the model call with LangSmith monitoring
            @langsmith_monitor.trace(run_type="llm", name="text_model_only", tags=["text", "query_only"])
            def generate_text_content(prompt):
                return text_model.generate_content(prompt)

            # Call the wrapped function
            response = generate_text_content(message)
            response_data['answer'] = response.text

            # Store the Q&A pair in AstraDB
            qa_vector = text_to_vector(message + " " + response_data['answer'])
            qa_metadata = {
                'source_type': 'direct_query',
                'source_id': None
            }
            qa_id = store_qa_pair(message, response_data['answer'], qa_vector, qa_metadata)
            if qa_id:
                logger.info(f"Stored direct Q&A pair in AstraDB with ID: {qa_id}")

        # Clean up temporary file if needed
        if file_path and os.path.exists(file_path):
            # Keep files for now for debugging purposes
            # In production, you might want to delete them or implement a cleanup job
            pass

        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in chat route: {str(e)}")
        logger.error(error_traceback)
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500
