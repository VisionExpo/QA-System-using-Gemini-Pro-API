"""
Flask Web App for QA System using Gemini Pro API
"""

from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import io
import base64
import uuid
import tempfile
import fitz  # PyMuPDF for PDF handling
import docx2txt  # For DOCX handling
import speech_recognition as sr  # For audio transcription
import mimetypes
import re
import json
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)

# Initialize models
text_model = genai.GenerativeModel('gemini-1.5-pro')
vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Using the recommended model

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# File processing functions
def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {str(e)}")
        return ""

def transcribe_audio(file_path):
    """Transcribe audio file to text"""
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return ""

def process_file(file):
    """Process uploaded file based on its type"""
    if not file:
        return None, None

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    mime_type = mimetypes.guess_type(file_path)[0]
    file_type = None
    extracted_content = None

    if mime_type:
        if mime_type.startswith('image/'):
            file_type = 'image'
            # We'll process the image directly in the chat route
            extracted_content = file_path
        elif mime_type == 'application/pdf':
            file_type = 'pdf'
            extracted_content = extract_text_from_pdf(file_path)
        elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
            file_type = 'docx'
            extracted_content = extract_text_from_docx(file_path)
        elif mime_type.startswith('audio/'):
            file_type = 'audio'
            extracted_content = transcribe_audio(file_path)
        else:
            file_type = 'unknown'
            extracted_content = f"Unsupported file type: {mime_type}"

    return file_type, extracted_content

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Initialize response
        response_data = {
            'answer': '',
            'error': None
        }

        # Get message from request
        message = request.form.get('message', '')

        # Check if there's a file in the request
        file_type = None
        file_content = None

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            print(f"Received file: {file.filename}")

            # Process the file based on its type
            file_type, file_content = process_file(file)
            print(f"File type: {file_type}")

            if not file_type or not file_content:
                return jsonify({'error': 'Failed to process the file'}), 400

        # Generate content based on message and file
        if file_type == 'image':
            # For images, use the vision model
            image = Image.open(file_content)
            print(f"Using vision model: {vision_model._model_name}")

            if message:
                print(f"Generating content with message and image")
                response = vision_model.generate_content([message, image])
            else:
                print(f"Generating content with image only")
                response = vision_model.generate_content(image)

            response_data['answer'] = response.text
        elif file_type in ['pdf', 'docx', 'audio']:
            # For text-based files, include the extracted content in the prompt
            combined_prompt = f"{message}\n\nContent extracted from {file_type.upper()} file:\n{file_content}"
            print(f"Using text model with extracted content from {file_type}")
            response = text_model.generate_content(combined_prompt)
            response_data['answer'] = response.text
        else:
            # Text-only query
            if not message.strip():
                return jsonify({'error': 'No message provided'}), 400

            print(f"Using text model for message: {message[:50]}...")
            response = text_model.generate_content(message)
            response_data['answer'] = response.text

        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in chat route: {str(e)}")
        print(error_traceback)
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

# Create templates directory and HTML files
os.makedirs('templates', exist_ok=True)

# Create index.html
with open('templates/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QA System using Gemini API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #4CAF50;
            text-align: center;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background-color: #e0e0e0;
            cursor: pointer;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
        }
        .tab.active {
            background-color: #4CAF50;
            color: white;
        }
        .tab-content {
            display: none;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 5px 5px 5px;
        }
        .tab-content.active {
            display: block;
        }
        textarea, input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #45a049;
        }
        .response {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 5px solid #4CAF50;
            border-radius: 5px;
            white-space: pre-wrap;
        }
        .loading {
            text-align: center;
            margin-top: 20px;
            display: none;
        }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #4CAF50;
            animation: spin 1s linear infinite;
            display: inline-block;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        #imagePreview {
            max-width: 100%;
            max-height: 300px;
            margin-top: 10px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>QA System using Gemini API</h1>

        <div class="tabs">
            <div class="tab active" onclick="openTab('textTab')">Text Q&A</div>
            <div class="tab" onclick="openTab('imageTab')">Image Analysis</div>
        </div>

        <div id="textTab" class="tab-content active">
            <h2>Ask a Question</h2>
            <textarea id="question" rows="5" placeholder="Enter your question here..."></textarea>
            <button onclick="askQuestion()">Get Answer</button>

            <div id="textLoading" class="loading">
                <div class="spinner"></div>
                <p>Generating answer...</p>
            </div>

            <div id="textResponse" class="response" style="display: none;"></div>
        </div>

        <div id="imageTab" class="tab-content">
            <h2>Analyze an Image</h2>
            <input type="text" id="prompt" placeholder="Enter your question about the image (optional)">
            <input type="file" id="imageFile" accept="image/*" onchange="previewImage()">
            <img id="imagePreview" src="" alt="Image Preview">
            <button onclick="analyzeImage()">Analyze Image</button>

            <div id="imageLoading" class="loading">
                <div class="spinner"></div>
                <p>Analyzing image...</p>
            </div>

            <div id="imageResponse" class="response" style="display: none;"></div>
        </div>
    </div>

    <script>
        function openTab(tabId) {
            // Hide all tab contents
            const tabContents = document.getElementsByClassName('tab-content');
            for (let i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }

            // Remove active class from all tabs
            const tabs = document.getElementsByClassName('tab');
            for (let i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }

            // Show the selected tab content and mark the tab as active
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        function askQuestion() {
            const question = document.getElementById('question').value.trim();
            if (!question) {
                alert('Please enter a question');
                return;
            }

            // Show loading spinner
            document.getElementById('textLoading').style.display = 'block';
            document.getElementById('textResponse').style.display = 'none';

            // Send request to server
            fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading spinner
                document.getElementById('textLoading').style.display = 'none';

                // Display response
                const responseElement = document.getElementById('textResponse');
                if (data.error) {
                    responseElement.innerHTML = `<strong>Error:</strong> ${data.error}`;
                } else {
                    responseElement.innerHTML = `<strong>Answer:</strong><br>${data.answer}`;
                }
                responseElement.style.display = 'block';
            })
            .catch(error => {
                // Hide loading spinner
                document.getElementById('textLoading').style.display = 'none';

                // Display error
                const responseElement = document.getElementById('textResponse');
                responseElement.innerHTML = `<strong>Error:</strong> ${error.message}`;
                responseElement.style.display = 'block';
            });
        }

        function previewImage() {
            const fileInput = document.getElementById('imageFile');
            const preview = document.getElementById('imagePreview');

            if (fileInput.files && fileInput.files[0]) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }

                reader.readAsDataURL(fileInput.files[0]);
            }
        }

        function analyzeImage() {
            const fileInput = document.getElementById('imageFile');
            if (!fileInput.files || !fileInput.files[0]) {
                alert('Please select an image');
                return;
            }

            const prompt = document.getElementById('prompt').value.trim();

            // Show loading spinner
            document.getElementById('imageLoading').style.display = 'block';
            document.getElementById('imageResponse').style.display = 'none';

            // Create form data
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('prompt', prompt);

            // Send request to server
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading spinner
                document.getElementById('imageLoading').style.display = 'none';

                // Display response
                const responseElement = document.getElementById('imageResponse');
                if (data.error) {
                    responseElement.innerHTML = `<strong>Error:</strong> ${data.error}`;
                } else {
                    responseElement.innerHTML = `<strong>Analysis:</strong><br>${data.analysis}`;
                }
                responseElement.style.display = 'block';
            })
            .catch(error => {
                // Hide loading spinner
                document.getElementById('imageLoading').style.display = 'none';

                // Display error
                const responseElement = document.getElementById('imageResponse');
                responseElement.innerHTML = `<strong>Error:</strong> ${error.message}`;
                responseElement.style.display = 'block';
            });
        }
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("Starting Flask app for QA System using Gemini API...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
