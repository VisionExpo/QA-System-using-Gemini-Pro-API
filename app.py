"""
QA System using Gemini Pro API
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)

# Initialize models
text_model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

# Define response functions
def get_text_response(prompt):
    """Get response from text model"""
    response = text_model.generate_content(prompt)
    return response

def get_vision_response(prompt, image):
    """Get response from vision model"""
    if prompt:
        response = vision_model.generate_content([prompt, image])
    else:
        response = vision_model.generate_content(image)
    return response

# Streamlit app
st.set_page_config(page_title="QA System using Gemini Pro", layout="wide")
st.title("QA System using Gemini Pro API")

# Sidebar
st.sidebar.title("Options")
app_mode = st.sidebar.radio("Select Mode", ["Text Q&A", "Image Analysis"])

if app_mode == "Text Q&A":
    st.header("Ask a Question")

    prompt = st.text_area("Enter your question:", height=150)

    if st.button("Get Answer"):
        if prompt:
            with st.spinner("Generating answer..."):
                try:
                    start_time = time.time()
                    response = get_text_response(prompt)
                    end_time = time.time()

                    st.subheader("Answer:")
                    st.write(response.text)

                    st.info(f"Answer generated in {end_time - start_time:.2f} seconds")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a question")

elif app_mode == "Image Analysis":
    st.header("Analyze an Image")

    prompt = st.text_input("Enter your question about the image (optional):")

    uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Analyze"):
            with st.spinner("Analyzing image..."):
                try:
                    start_time = time.time()
                    response = get_vision_response(prompt, image)
                    end_time = time.time()

                    st.subheader("Analysis:")
                    st.write(response.text)

                    st.info(f"Analysis completed in {end_time - start_time:.2f} seconds")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("QA System using Gemini Pro API - v1.0.0")
