"""
YouTube video processing utilities for QA System using Gemini API
Handles downloading and transcribing YouTube videos
"""

import os
import re
import logging
import tempfile
from pytube import YouTube
from urllib.parse import urlparse, parse_qs

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import speech recognition with error handling
try:
    import speech_recognition as sr
    sr_available = True
except ImportError:
    sr_available = False
    logger.warning("SpeechRecognition not installed. Audio transcription will be limited.")

def is_youtube_url(url):
    """Check if a URL is a valid YouTube URL"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    youtube_regex_match = re.match(youtube_regex, url)
    return bool(youtube_regex_match)

def extract_video_id(url):
    """Extract the video ID from a YouTube URL"""
    if 'youtu.be' in url:
        # Handle youtu.be URLs
        parsed_url = urlparse(url)
        video_id = parsed_url.path.lstrip('/')
        # Remove any additional parameters
        video_id = video_id.split('/')[0]
        return video_id
    else:
        # Handle youtube.com URLs
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]

def get_video_info(url):
    """Get basic information about a YouTube video"""
    try:
        logger.info(f"Getting info for YouTube video: {url}")
        yt = YouTube(url)
        
        info = {
            'title': yt.title,
            'author': yt.author,
            'length_seconds': yt.length,
            'views': yt.views,
            'description': yt.description,
            'thumbnail_url': yt.thumbnail_url,
            'publish_date': str(yt.publish_date) if yt.publish_date else None,
            'video_id': extract_video_id(url)
        }
        
        logger.info(f"Successfully retrieved info for video: {info['title']}")
        return info
    except Exception as e:
        logger.error(f"Error getting YouTube video info: {str(e)}")
        return {'error': str(e)}

def download_audio(url, output_path=None):
    """Download the audio from a YouTube video"""
    try:
        logger.info(f"Downloading audio from YouTube video: {url}")
        yt = YouTube(url)
        
        # Get the audio stream with the highest quality
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if not audio_stream:
            logger.error("No audio stream found for this video")
            return None
        
        # Create a temporary file if no output path is provided
        if not output_path:
            temp_dir = tempfile.gettempdir()
            video_id = extract_video_id(url)
            output_path = os.path.join(temp_dir, f"{video_id}.mp4")
        
        # Download the audio
        audio_stream.download(output_path=os.path.dirname(output_path), 
                             filename=os.path.basename(output_path))
        
        logger.info(f"Successfully downloaded audio to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error downloading YouTube audio: {str(e)}")
        return None

def transcribe_youtube_audio(url):
    """Download and transcribe a YouTube video"""
    if not sr_available:
        logger.error("SpeechRecognition not installed. Cannot transcribe audio.")
        return "Cannot transcribe YouTube videos. SpeechRecognition library not installed."
    
    try:
        logger.info(f"Transcribing YouTube video: {url}")
        
        # Get video info
        video_info = get_video_info(url)
        if 'error' in video_info:
            return f"Error getting video info: {video_info['error']}"
        
        # Check if video is too long (>10 minutes)
        if video_info['length_seconds'] > 600:
            logger.warning(f"Video is too long ({video_info['length_seconds']} seconds). Only transcribing first 10 minutes.")
        
        # Download audio
        audio_path = download_audio(url)
        if not audio_path:
            return "Failed to download audio from YouTube video."
        
        # Transcribe audio
        recognizer = sr.Recognizer()
        
        # Convert to WAV for SpeechRecognition
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
        os.system(f'ffmpeg -i "{audio_path}" -ar 16000 -ac 1 "{temp_wav}" -y -loglevel quiet')
        
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        # Clean up temporary files
        os.remove(audio_path)
        os.remove(temp_wav)
        
        # Prepare result
        result = {
            'title': video_info['title'],
            'author': video_info['author'],
            'transcript': text,
            'video_id': video_info['video_id'],
            'length_seconds': video_info['length_seconds']
        }
        
        logger.info(f"Successfully transcribed YouTube video: {video_info['title']}")
        return result
    except Exception as e:
        logger.error(f"Error transcribing YouTube video: {str(e)}")
        return f"Error transcribing YouTube video: {str(e)}"

def get_youtube_transcript(url):
    """Get transcript for a YouTube video using pytube and transcription"""
    if not is_youtube_url(url):
        return f"Not a valid YouTube URL: {url}"
    
    try:
        # First try to get video info
        video_info = get_video_info(url)
        if 'error' in video_info:
            return f"Error getting video info: {video_info['error']}"
        
        # Create a summary of the video
        video_summary = (
            f"Title: {video_info['title']}\n"
            f"Author: {video_info['author']}\n"
            f"Length: {video_info['length_seconds']} seconds\n"
            f"Views: {video_info['views']}\n"
            f"Description: {video_info['description']}\n\n"
        )
        
        # Try to transcribe the video
        if sr_available:
            transcript_result = transcribe_youtube_audio(url)
            if isinstance(transcript_result, dict) and 'transcript' in transcript_result:
                return video_summary + "Transcript:\n" + transcript_result['transcript']
            else:
                return video_summary + f"Transcription failed: {transcript_result}"
        else:
            return video_summary + "Transcription not available. SpeechRecognition library not installed."
    except Exception as e:
        logger.error(f"Error processing YouTube video: {str(e)}")
        return f"Error processing YouTube video: {str(e)}"

if __name__ == "__main__":
    # Test the module
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(get_youtube_transcript(test_url))
