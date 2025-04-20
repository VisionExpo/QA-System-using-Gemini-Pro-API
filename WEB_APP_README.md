# QA System Web App using Gemini API

A web application for question answering and image analysis using Google's Gemini API.

## Features

- **Text Q&A**: Ask questions and get detailed answers from Gemini 1.5 Pro
- **Image Analysis**: Upload images and get AI-powered analysis using Gemini 1.5 Pro Vision
- **User-friendly Interface**: Clean, responsive Streamlit interface
- **Environment Variable Support**: Secure API key management

## Screenshots

(Add screenshots of your application here)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/QA-System-using-Gemini-Pro-API.git
   cd QA-System-using-Gemini-Pro-API
   ```

2. Create and activate a virtual environment:

   **For Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **For macOS/Linux:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:

   Create a `.env` file with your Google API key:

   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

   You can get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## Usage

Run the web application:

```bash
streamlit run web_app.py
```

This will start the Streamlit server and open the application in your web browser.

### Text Q&A Mode

1. Select "Text Q&A" from the sidebar
2. Enter your question in the text area
3. Click "Get Answer" to receive a response from the Gemini 1.5 Pro model

### Image Analysis Mode

1. Select "Image Analysis" from the sidebar
2. Optionally, enter a question about the image
3. Upload an image using the file uploader
4. Click "Analyze Image" to get the AI's analysis of the image

## Troubleshooting

- If you encounter an error about the API key, make sure your `.env` file is properly set up with a valid API key.
- If you get model-related errors, check that the models specified in the code are available in your Google AI Studio account.
- For other issues, check the Streamlit and Google Generative AI documentation.

## License

MIT License
