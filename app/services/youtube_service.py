"""
YouTube processing service for the QA System
"""

import logging
import google.generativeai as genai

# Set up logging
logger = logging.getLogger(__name__)

# Initialize models
text_model = genai.GenerativeModel('gemini-1.5-pro')

def summarize_youtube_video(url, transcript):
    """Generate a summary of a YouTube video using Gemini"""
    try:
        # Check if transcript contains error messages
        contains_error = any(error_text in transcript for error_text in [
            "Error processing YouTube video",
            "Transcription failed",
            "Transcription not attempted",
            "Transcription not available"
        ])
        
        # Create a prompt for summarization
        if contains_error:
            # If there are errors, ask Gemini to provide information about the video instead
            prompt = f"""
            I tried to access information about a YouTube video but encountered some issues.
            Here's what I was able to retrieve:
            
            {transcript}
            
            Based on this limited information and your knowledge about this video or similar content:
            1. Can you provide any additional context about what this video might be about?
            2. What topics might be covered in a video like this?
            3. What would be helpful to know about this subject?
            
            Please note that you may not have specific information about this exact video,
            so provide general information that would be helpful to someone interested in this topic.
            """
        else:
            # Normal summarization prompt
            prompt = f"""
            Please provide a comprehensive summary of the following YouTube video transcript.
            Focus on the main points, key insights, and important details.
            
            Video URL: {url}
            
            Transcript:
            {transcript[:10000]}  # Limit transcript length to avoid token limits
            
            Please structure your summary with:
            1. A brief overview (1-2 sentences)
            2. Main topics covered
            3. Key points and insights
            4. Conclusion or takeaways
            """
        
        # Generate summary
        response = text_model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        logger.error(f"Error summarizing YouTube video: {str(e)}")
        return f"Error generating summary: {str(e)}\n\nI couldn't access this YouTube video properly. Please provide more details about what you're looking for, and I'll try to help based on general knowledge."
