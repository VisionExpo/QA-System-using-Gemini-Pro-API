"""
Example application using LLM Monitor
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

from src.llm_monitor.utils.logger import LLMLogger
from src.llm_monitor.components.monitor import LLMMonitor
from src.llm_monitor.config.configuration import ConfigurationManager

# Load environment variables
load_dotenv()

# Initialize logger
logger = LLMLogger(log_dir="logs", module_name="llm_app")
logger.info("Starting LLM application")

# Load configuration
config_manager = ConfigurationManager()
config = config_manager.get_config()
logger.info(f"Loaded configuration for project: {config.project_name}")

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.error("GOOGLE_API_KEY environment variable not set")
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)

# Initialize monitors
text_monitor = LLMMonitor(
    model_name="gemini-pro",
    logger=logger,
    log_dir="logs/gemini-pro",
    track_latency=True,
    track_tokens=True,
    track_inputs=True,
    track_outputs=True
)

vision_monitor = LLMMonitor(
    model_name="gemini-pro-vision",
    logger=logger,
    log_dir="logs/gemini-pro-vision",
    track_latency=True,
    track_tokens=False,  # Token tracking not available for vision model
    track_inputs=True,
    track_outputs=True
)

# Initialize models
text_model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

# Define monitored functions
@text_monitor.monitor
def get_text_response(prompt):
    """Get response from text model"""
    response = text_model.generate_content(prompt)
    return response

@vision_monitor.monitor
def get_vision_response(prompt, image):
    """Get response from vision model"""
    if prompt:
        response = vision_model.generate_content([prompt, image])
    else:
        response = vision_model.generate_content(image)
    return response

# Streamlit app
st.set_page_config(page_title="LLM Monitor Demo", layout="wide")
st.title("LLM Monitor Demo")

# Sidebar
st.sidebar.title("Options")
app_mode = st.sidebar.radio("Select Mode", ["Text", "Vision"])

if app_mode == "Text":
    st.header("Text Generation")
    
    prompt = st.text_area("Enter your prompt:", height=150)
    
    if st.button("Generate"):
        if prompt:
            with st.spinner("Generating response..."):
                try:
                    start_time = time.time()
                    response = get_text_response(prompt)
                    end_time = time.time()
                    
                    st.subheader("Response:")
                    st.write(response.text)
                    
                    st.info(f"Response generated in {end_time - start_time:.2f} seconds")
                    
                    # Display metrics
                    if hasattr(response, "usage") and response.usage:
                        st.subheader("Metrics:")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Input Tokens", getattr(response.usage, "prompt_tokens", "N/A"))
                        col2.metric("Output Tokens", getattr(response.usage, "completion_tokens", "N/A"))
                        col3.metric("Total Tokens", getattr(response.usage, "total_tokens", "N/A"))
                    
                except Exception as e:
                    logger.error(f"Error generating text response: {str(e)}")
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a prompt")

elif app_mode == "Vision":
    st.header("Vision Analysis")
    
    prompt = st.text_input("Enter your prompt (optional):")
    
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
                    logger.error(f"Error generating vision response: {str(e)}")
                    st.error(f"Error: {str(e)}")

# Display metrics summary
if st.sidebar.button("Show Metrics Summary"):
    st.sidebar.subheader("Text Model Metrics")
    text_metrics = text_monitor.get_metrics_summary()
    
    if "metrics" in text_metrics:
        metrics = text_metrics["metrics"]
        for key, value in metrics.items():
            if isinstance(value, float):
                st.sidebar.text(f"{key}: {value:.2f}")
            else:
                st.sidebar.text(f"{key}: {value}")
    else:
        st.sidebar.text("No metrics collected yet")
    
    st.sidebar.subheader("Vision Model Metrics")
    vision_metrics = vision_monitor.get_metrics_summary()
    
    if "metrics" in vision_metrics:
        metrics = vision_metrics["metrics"]
        for key, value in metrics.items():
            if isinstance(value, float):
                st.sidebar.text(f"{key}: {value:.2f}")
            else:
                st.sidebar.text(f"{key}: {value}")
    else:
        st.sidebar.text("No metrics collected yet")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("LLM Monitor Demo - v0.1.0")

logger.info("Application initialized successfully")
