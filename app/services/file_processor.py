"""
File processing utilities for QA System using Gemini API
Handles conversion of various file types to text or vector representations
"""

import os
import io
import tempfile
import mimetypes
import logging
import re
from urllib.parse import urlparse

# Set up logging
logger = logging.getLogger(__name__)

# Import libraries with error handling
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logger.warning("PyMuPDF (fitz) not installed. PDF processing will be unavailable.")

try:
    import docx
except ImportError:
    docx = None
    logger.warning("python-docx not installed. DOCX processing will be unavailable.")

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    logger.warning("SpeechRecognition not installed. Audio transcription will be unavailable.")

# For video processing, we'll use a flag to indicate whether it's available
# This avoids the need for ffmpeg to be installed
video_processing_available = False
logger.warning("Video processing disabled for simplicity. Install ffmpeg and moviepy for full video support.")

# Import YouTube processor with error handling
try:
    from app.services.youtube_processor import get_youtube_transcript, is_youtube_url
    youtube_available = True
except ImportError:
    youtube_available = False
    logger.warning("YouTube processor not available. YouTube video processing will be unavailable.")
from PIL import Image
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize the sentence transformer model lazily
sentence_model = None

def get_sentence_model():
    """Lazily load the sentence transformer model only when needed"""
    global sentence_model
    if sentence_model is None:
        try:
            logger.info("Loading sentence transformer model (lazy initialization)...")
            # Use a model with 1024 dimensions to match AstraDB collection
            sentence_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
            logger.info("Sentence transformer model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sentence transformer model: {str(e)}")
            return None
    return sentence_model

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    if not fitz:
        logger.error("PyMuPDF (fitz) not installed. Cannot extract text from PDF.")
        return "[PDF text extraction not available. PyMuPDF not installed.]"

    try:
        logger.info(f"Extracting text from PDF: {file_path}")
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return f"[Error extracting text from PDF: {str(e)}]"

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    if not docx:
        logger.error("python-docx not installed. Cannot extract text from DOCX.")
        return "[DOCX text extraction not available. python-docx not installed.]"

    try:
        logger.info(f"Extracting text from DOCX: {file_path}")
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        logger.info(f"Successfully extracted {len(text)} characters from DOCX")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        return f"[Error extracting text from DOCX: {str(e)}]"

def transcribe_audio(file_path):
    """Transcribe audio file to text"""
    if not sr:
        logger.error("SpeechRecognition not installed. Cannot transcribe audio.")
        return "[Audio transcription not available. SpeechRecognition not installed.]"

    try:
        logger.info(f"Transcribing audio: {file_path}")
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        logger.info(f"Successfully transcribed audio to {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return f"[Error transcribing audio: {str(e)}]"

def extract_audio_from_video(file_path):
    """Extract audio from video file and transcribe it"""
    if not video_processing_available:
        logger.error("Video processing not available.")
        return "[Video processing not available. Install ffmpeg and moviepy for full video support.]"

    if not sr:
        logger.error("SpeechRecognition not installed. Cannot transcribe audio from video.")
        return "[Audio transcription not available. SpeechRecognition not installed.]"

    try:
        logger.info(f"Extracting audio from video: {file_path}")
        # Since video processing is disabled, we'll return a placeholder message
        return "[Video processing is currently disabled. Install ffmpeg and moviepy for full video support.]"
    except Exception as e:
        logger.error(f"Error extracting audio from video: {str(e)}")
        return f"[Error extracting audio from video: {str(e)}]"

def describe_image(image_path):
    """Generate a basic description of an image (placeholder for actual image analysis)"""
    try:
        logger.info(f"Analyzing image: {image_path}")
        img = Image.open(image_path)
        width, height = img.size
        mode = img.mode
        format_type = img.format

        description = f"Image analysis: {width}x{height} {format_type} image in {mode} mode."
        logger.info(f"Generated basic image description")
        return description
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return f"[Error analyzing image: {str(e)}]"

def text_to_vector(text):
    """Convert text to vector representation using sentence transformers"""
    try:
        # Get the model (will be lazily loaded if not already loaded)
        model = get_sentence_model()
        if not model:
            logger.warning("Sentence transformer model not available")
            return np.zeros(1024)  # Return zero vector as fallback

        # Handle empty or None text
        if not text:
            logger.warning("Empty or None text provided to text_to_vector")
            # Return a zero vector of the expected dimension
            return np.zeros(1024)

        logger.info(f"Converting {len(text)} characters to vector representation")
        # For long texts, we'll chunk and average the embeddings
        max_length = 512  # Typical max length for transformer models
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]

        # Get embeddings for each chunk
        embeddings = model.encode(chunks)

        # Average the embeddings
        if len(embeddings) > 1:
            vector = np.mean(embeddings, axis=0)
        else:
            vector = embeddings[0]

        logger.info(f"Successfully converted text to vector of dimension {vector.shape}")
        return vector
    except Exception as e:
        logger.error(f"Error converting text to vector: {str(e)}")
        # Return a zero vector of the expected dimension instead of None
        logger.info("Returning zero vector as fallback")
        return np.zeros(1024)

def process_youtube_url(url):
    """Process a YouTube URL and return transcript and vector representation"""
    if not youtube_available:
        logger.error("YouTube processor not available. Cannot process YouTube URL.")
        return {
            "file_type": "youtube",
            "text": "YouTube processing not available. Please install pytube package.",
            "vector": None,
            "error": "YouTube processor not available"
        }

    try:
        logger.info(f"Processing YouTube URL: {url}")

        # Check if it's a valid YouTube URL
        if not is_youtube_url(url):
            logger.error(f"Not a valid YouTube URL: {url}")
            return {
                "file_type": "youtube",
                "text": f"Not a valid YouTube URL: {url}",
                "vector": None,
                "error": "Invalid YouTube URL"
            }

        # Get transcript
        transcript = get_youtube_transcript(url)

        # Initialize result
        result = {
            "file_type": "youtube",
            "text": transcript,
            "vector": None,
            "error": None,
            "url": url
        }

        # Generate vector representation
        if transcript and not isinstance(transcript, str) or (isinstance(transcript, str) and not transcript.startswith("Error")):
            result["vector"] = text_to_vector(transcript)
        else:
            result["error"] = "Failed to get transcript"

        return result
    except Exception as e:
        logger.error(f"Error processing YouTube URL: {str(e)}")
        return {
            "file_type": "youtube",
            "text": f"Error processing YouTube URL: {str(e)}",
            "vector": None,
            "error": str(e),
            "url": url
        }

def is_url(text):
    """Check if a string is a URL"""
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False

def process_file(file_path):
    """Process file based on its type and return text content and vector representation"""
    # Check if it's a URL instead of a file path
    if isinstance(file_path, str) and is_url(file_path):
        # Check if it's a YouTube URL
        if youtube_available and is_youtube_url(file_path):
            return process_youtube_url(file_path)
        else:
            logger.error(f"Unsupported URL type: {file_path}")
            return {
                "file_type": "url",
                "text": f"Unsupported URL type: {file_path}",
                "vector": None,
                "error": "Unsupported URL type"
            }

    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {"error": "File not found", "text": None, "vector": None}

        mime_type = mimetypes.guess_type(file_path)[0]
        file_extension = os.path.splitext(file_path)[1].lower()

        logger.info(f"Processing file: {file_path} (MIME: {mime_type}, Extension: {file_extension})")

        # Initialize result
        result = {
            "file_type": None,
            "text": None,
            "vector": None,
            "error": None
        }

        # Process based on file type
        if mime_type:
            if mime_type.startswith('image/'):
                result["file_type"] = 'image'
                # For images, we just return the path - actual processing will be done by Gemini
                result["text"] = describe_image(file_path)
            elif mime_type == 'application/pdf' or file_extension == '.pdf':
                result["file_type"] = 'pdf'
                result["text"] = extract_text_from_pdf(file_path)
            elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'] or file_extension in ['.docx', '.doc']:
                result["file_type"] = 'docx'
                result["text"] = extract_text_from_docx(file_path)
            elif mime_type.startswith('audio/') or file_extension in ['.mp3', '.wav', '.ogg', '.flac']:
                result["file_type"] = 'audio'
                result["text"] = transcribe_audio(file_path)
            elif mime_type.startswith('video/') or file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
                result["file_type"] = 'video'
                result["text"] = extract_audio_from_video(file_path)
            else:
                result["file_type"] = 'unknown'
                result["text"] = f"Unsupported file type: {mime_type}"
                result["error"] = "Unsupported file type"
        else:
            result["file_type"] = 'unknown'
            result["text"] = f"Unknown file type for file: {file_path}"
            result["error"] = "Unknown file type"

        # Generate vector representation if we have text
        if result["text"] and not result["error"]:
            result["vector"] = text_to_vector(result["text"])

        return result
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {
            "file_type": "error",
            "text": f"Error processing file: {str(e)}",
            "vector": None,
            "error": str(e)
        }
