"""
Flask Web App for QA System using Gemini Pro API
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import io
import base64

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

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    try:
        response = text_model.generate_content(question)
        return jsonify({'answer': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    prompt = request.form.get('prompt', '')

    try:
        # Print debug information
        print(f"Received image: {image_file.filename}")
        print(f"Prompt: {prompt}")

        # Open and process the image
        image = Image.open(image_file)

        # Check if the model is available
        print(f"Using vision model: {vision_model._model_name}")

        # Generate content
        if prompt:
            print(f"Generating content with prompt and image")
            response = vision_model.generate_content([prompt, image])
        else:
            print(f"Generating content with image only")
            response = vision_model.generate_content(image)

        # Return the response
        return jsonify({'analysis': response.text})
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in analyze route: {str(e)}")
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
