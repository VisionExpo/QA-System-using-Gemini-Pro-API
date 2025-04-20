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

# Create directories for templates and static files
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Create CSS file
with open('static/css/style.css', 'w') as f:
    f.write('''
/* Base styles */
:root {
    --primary-color: #10a37f;
    --secondary-color: #f7f7f8;
    --text-color: #343541;
    --light-text: #6e6e80;
    --border-color: #e5e5e5;
    --hover-color: #0d8c6f;
    --shadow-color: rgba(0, 0, 0, 0.1);
    --user-msg-bg: #f7f7f8;
    --ai-msg-bg: #ffffff;
    --error-color: #ff4d4f;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--secondary-color);
    height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header */
.header {
    background-color: #ffffff;
    padding: 1rem 2rem;
    box-shadow: 0 2px 5px var(--shadow-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 10;
}

.header h1 {
    color: var(--primary-color);
    font-size: 1.5rem;
    font-weight: 600;
}

.header-actions {
    display: flex;
    gap: 1rem;
}

/* Main container */
.container {
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    flex: 1;
    display: flex;
    flex-direction: column;
    height: calc(100vh - 70px);
}

/* Chat area */
.chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    scroll-behavior: smooth;
}

.message {
    display: flex;
    margin-bottom: 1.5rem;
    animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message-content {
    max-width: 80%;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 2px var(--shadow-color);
}

.user-message {
    justify-content: flex-end;
}

.user-message .message-content {
    background-color: var(--user-msg-bg);
    border: 1px solid var(--border-color);
}

.ai-message {
    justify-content: flex-start;
}

.ai-message .message-content {
    background-color: var(--ai-msg-bg);
    border-left: 4px solid var(--primary-color);
}

.message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin: 0 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
}

.user-avatar {
    background-color: #4a7aff;
}

.ai-avatar {
    background-color: var(--primary-color);
}

/* Input area */
.chat-input-container {
    padding: 1rem;
    background-color: #ffffff;
    border-top: 1px solid var(--border-color);
    position: relative;
}

.chat-form {
    display: flex;
    flex-direction: column;
}

.input-group {
    display: flex;
    position: relative;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    background-color: #ffffff;
    transition: border-color 0.3s;
}

.input-group:focus-within {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
}

.chat-input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 0.5rem;
    font-size: 1rem;
    resize: none;
    max-height: 200px;
    min-height: 56px;
    outline: none;
    font-family: inherit;
}

.chat-input::placeholder {
    color: var(--light-text);
}

.input-buttons {
    display: flex;
    align-items: center;
    padding-right: 0.5rem;
}

.file-upload {
    position: relative;
    margin-right: 0.5rem;
}

.file-upload input[type="file"] {
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
}

.file-upload-btn {
    background: none;
    border: none;
    color: var(--light-text);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 0.25rem;
    transition: background-color 0.3s;
}

.file-upload-btn:hover {
    background-color: var(--secondary-color);
}

.send-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.3s;
}

.send-btn:hover {
    background-color: var(--hover-color);
}

.send-btn:disabled {
    background-color: var(--border-color);
    cursor: not-allowed;
}

/* File preview */
.file-preview {
    margin-top: 0.5rem;
    display: none;
    align-items: center;
    background-color: var(--secondary-color);
    padding: 0.5rem;
    border-radius: 0.25rem;
    animation: slideUp 0.3s ease-in-out;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.file-preview.show {
    display: flex;
}

.file-preview img {
    max-height: 100px;
    max-width: 100px;
    border-radius: 0.25rem;
    object-fit: cover;
}

.file-info {
    margin-left: 0.5rem;
    flex: 1;
}

.file-name {
    font-weight: 500;
    word-break: break-all;
}

.file-type {
    color: var(--light-text);
    font-size: 0.875rem;
}

.remove-file {
    background: none;
    border: none;
    color: var(--light-text);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 0.25rem;
    transition: color 0.3s;
}

.remove-file:hover {
    color: var(--error-color);
}

/* Loading indicator */
.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

.typing-indicator {
    display: flex;
    align-items: center;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background-color: var(--light-text);
    border-radius: 50%;
    margin: 0 2px;
    animation: typingAnimation 1.5s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typingAnimation {
    0% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
    100% { transform: translateY(0); }
}

/* Responsive design */
@media (max-width: 768px) {
    .header {
        padding: 0.75rem 1rem;
    }

    .header h1 {
        font-size: 1.25rem;
    }

    .message-content {
        max-width: 90%;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --primary-color: #19c37d;
        --secondary-color: #343541;
        --text-color: #f1f1f3;
        --light-text: #acacbe;
        --border-color: #4d4d4f;
        --hover-color: #2a9d8f;
        --shadow-color: rgba(0, 0, 0, 0.3);
        --user-msg-bg: #444654;
        --ai-msg-bg: #343541;
    }

    body {
        background-color: #202123;
    }

    .header {
        background-color: #202123;
    }

    .chat-input-container {
        background-color: #202123;
    }

    .input-group {
        background-color: #343541;
    }

    .chat-input {
        background-color: #343541;
        color: var(--text-color);
    }
}
''')
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
