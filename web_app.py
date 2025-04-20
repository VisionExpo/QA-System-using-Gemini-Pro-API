"""
Web App for QA System using Gemini Pro API
"""

import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY environment variable not set. Please set it in your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# Set page configuration
st.set_page_config(
    page_title="QA System using Gemini API",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize models
@st.cache_resource
def get_models():
    text_model = genai.GenerativeModel('gemini-1.5-pro')
    vision_model = genai.GenerativeModel('gemini-1.5-pro-vision-latest')
    return text_model, vision_model

text_model, vision_model = get_models()

# Define functions for getting responses
def get_text_response(prompt):
    """Get response from text model"""
    try:
        response = text_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_vision_response(prompt, image):
    """Get response from vision model"""
    try:
        if prompt:
            response = vision_model.generate_content([prompt, image])
        else:
            response = vision_model.generate_content(image)
        return response.text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2196F3;
        margin-bottom: 1rem;
    }
    .response-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Main app
st.markdown("<h1 class='main-header'>QA System using Gemini API</h1>", unsafe_allow_html=True)
st.markdown("Ask questions or analyze images using Google's Gemini AI models.")

# Sidebar
st.sidebar.title("Options")
app_mode = st.sidebar.radio("Select Mode", ["Text Q&A", "Image Analysis"])

# Text Q&A Mode
if app_mode == "Text Q&A":
    st.markdown("<h2 class='sub-header'>Ask a Question</h2>", unsafe_allow_html=True)
    
    # Input area
    question = st.text_area("Enter your question:", height=150, 
                           placeholder="e.g., What are the main features of Python programming language?")
    
    # Submit button
    if st.button("Get Answer"):
        if question:
            with st.spinner("Generating answer..."):
                answer = get_text_response(question)
                
                if answer:
                    st.markdown("<div class='response-container'>", unsafe_allow_html=True)
                    st.markdown("### Answer:")
                    st.markdown(answer)
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter a question.")

# Image Analysis Mode
elif app_mode == "Image Analysis":
    st.markdown("<h2 class='sub-header'>Analyze an Image</h2>", unsafe_allow_html=True)
    
    # Input area for prompt
    prompt = st.text_input("Enter your question about the image (optional):", 
                          placeholder="e.g., What's in this image? or What breed is this dog?")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Submit button
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                answer = get_vision_response(prompt, image)
                
                if answer:
                    st.markdown("<div class='response-container'>", unsafe_allow_html=True)
                    st.markdown("### Analysis:")
                    st.markdown(answer)
                    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("QA System using Gemini API - v1.0.0")
st.sidebar.markdown("Built with Streamlit and Google's Gemini API")
