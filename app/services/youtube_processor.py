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
        # Clean the URL - remove any extra parameters after the video ID
        clean_url = url.split('&')[0] if '&' in url else url
        logger.info(f"Getting info for YouTube video: {clean_url}")

        # Add a timeout to avoid hanging
        yt = YouTube(clean_url, use_oauth=False, allow_oauth_cache=False)

        # Try to get video info with error handling for each attribute
        try:
            title = yt.title
        except Exception:
            title = "[Title unavailable]"

        try:
            author = yt.author
        except Exception:
            author = "[Author unavailable]"

        try:
            length_seconds = yt.length
        except Exception:
            length_seconds = 0

        try:
            views = yt.views
        except Exception:
            views = 0

        try:
            description = yt.description
        except Exception:
            description = "[Description unavailable]"

        try:
            thumbnail_url = yt.thumbnail_url
        except Exception:
            thumbnail_url = None

        try:
            publish_date = str(yt.publish_date) if yt.publish_date else None
        except Exception:
            publish_date = None

        video_id = extract_video_id(clean_url)

        info = {
            'title': title,
            'author': author,
            'length_seconds': length_seconds,
            'views': views,
            'description': description,
            'thumbnail_url': thumbnail_url,
            'publish_date': publish_date,
            'video_id': video_id,
            'url': clean_url
        }

        logger.info(f"Successfully retrieved info for video: {info['title']}")
        return info
    except Exception as e:
        logger.error(f"Error getting YouTube video info: {str(e)}")
        return {
            'error': str(e),
            'url': url,
            'video_id': extract_video_id(url) if is_youtube_url(url) else None,
            'title': "[Unable to access video]",
            'description': f"Error accessing video: {str(e)}"
        }

def download_audio(url, output_path=None, max_retries=3):
    """Download the audio from a YouTube video with retries and error handling"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading audio from YouTube video: {url} (Attempt {attempt+1}/{max_retries})")

            # Clean the URL by removing any parameters after the video ID
            clean_url = url.split('&')[0] if '&' in url else url

            # Add options to avoid age restriction issues
            yt = YouTube(
                clean_url,
                use_oauth=False,
                allow_oauth_cache=False
            )

            # Get the audio stream with the highest quality
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

            if not audio_stream:
                logger.error("No audio stream found for this video")
                return None

            # Create a temporary file if no output path is provided
            if not output_path:
                temp_dir = tempfile.gettempdir()
                video_id = extract_video_id(clean_url)
                output_path = os.path.join(temp_dir, f"{video_id}.mp4")

            # Download the audio
            audio_stream.download(output_path=os.path.dirname(output_path),
                                filename=os.path.basename(output_path))

            logger.info(f"Successfully downloaded audio to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error downloading YouTube audio (Attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                # Wait before retrying (exponential backoff)
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                import time
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to download audio after {max_retries} attempts")
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
        # Clean the URL - remove any extra parameters after the video ID
        clean_url = url.split('&')[0] if '&' in url else url

        # First try to get video info
        video_info = get_video_info(clean_url)

        # Create a summary of the video
        video_summary = "YouTube Video Information:\n"

        if 'error' in video_info:
            video_summary += f"Warning: Limited information available. Error: {video_info['error']}\n\n"

        video_summary += (
            f"Title: {video_info.get('title', '[Title unavailable]')}\n"
            f"Author: {video_info.get('author', '[Author unavailable]')}\n"
            f"Video ID: {video_info.get('video_id', '[ID unavailable]')}\n"
        )

        if video_info.get('length_seconds', 0) > 0:
            video_summary += f"Length: {video_info.get('length_seconds')} seconds\n"

        if video_info.get('views', 0) > 0:
            video_summary += f"Views: {video_info.get('views')}\n"

        if video_info.get('description'):
            # Truncate description if it's too long
            desc = video_info.get('description', '')
            if len(desc) > 500:
                desc = desc[:500] + "..."
            video_summary += f"Description: {desc}\n"

        video_summary += "\n"

        # Try to transcribe the video if no error in video info and SpeechRecognition is available
        transcription_success = False
        if 'error' not in video_info and sr_available:
            try:
                logger.info(f"Attempting to transcribe video: {clean_url}")
                transcript_result = transcribe_youtube_audio(clean_url)
                if isinstance(transcript_result, dict) and 'transcript' in transcript_result:
                    video_summary += "Transcript:\n" + transcript_result['transcript']
                    transcription_success = True
                else:
                    logger.warning(f"Transcription failed: {transcript_result}")
                    video_summary += f"Transcription failed: {transcript_result}\n"
            except Exception as e:
                logger.error(f"Error transcribing video: {str(e)}")
                video_summary += f"Transcription failed: {str(e)}\n"
        else:
            if 'error' in video_info:
                video_summary += "\nTranscription not attempted due to error accessing video.\n"
            else:
                video_summary += "\nTranscription not available. SpeechRecognition library not installed.\n"

        # Add a note about using the description as a fallback
        if not transcription_success and video_info.get('description'):
            video_summary += "\nUsing video description as a fallback since transcription was not available:\n\n"
            # Include the full description now
            video_summary += video_info.get('description', '')

        # Add a prompt for the user
        video_summary += "\n\nPlease provide a summary of what you'd like to know about this video."

        return video_summary
    except Exception as e:
        logger.error(f"Error processing YouTube video: {str(e)}")
        return f"Error processing YouTube video: {str(e)}\n\nPlease provide a summary of what you'd like to know about this video instead."
