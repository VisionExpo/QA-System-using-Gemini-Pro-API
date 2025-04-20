"""
Script to download and set up FFmpeg for video processing
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from urllib.request import urlretrieve

def download_ffmpeg():
    """Download and set up FFmpeg for the current platform"""
    system = platform.system().lower()
    
    if system == "windows":
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        print(f"Downloading FFmpeg for Windows from {url}...")
    elif system == "darwin":  # macOS
        url = "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
        print(f"Downloading FFmpeg for macOS from {url}...")
    elif system == "linux":
        print("On Linux, it's recommended to install FFmpeg using your package manager:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  Fedora: sudo dnf install ffmpeg")
        print("  Arch Linux: sudo pacman -S ffmpeg")
        return
    else:
        print(f"Unsupported platform: {system}")
        return
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "ffmpeg.zip")
    
    try:
        # Download the zip file
        print("Downloading FFmpeg...")
        urlretrieve(url, zip_path)
        
        # Extract the zip file
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the ffmpeg executable
        ffmpeg_exe = None
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.startswith("ffmpeg") and (file.endswith(".exe") or "." not in file):
                    ffmpeg_exe = os.path.join(root, file)
                    break
            if ffmpeg_exe:
                break
        
        if not ffmpeg_exe:
            print("Could not find ffmpeg executable in the downloaded package.")
            return
        
        # Create bin directory if it doesn't exist
        bin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin")
        os.makedirs(bin_dir, exist_ok=True)
        
        # Copy ffmpeg to bin directory
        dest_path = os.path.join(bin_dir, os.path.basename(ffmpeg_exe))
        shutil.copy2(ffmpeg_exe, dest_path)
        
        # Make executable on Unix-like systems
        if system != "windows":
            os.chmod(dest_path, 0o755)
        
        print(f"FFmpeg installed successfully at: {dest_path}")
        print("You can now use video processing features in the QA System.")
        
    except Exception as e:
        print(f"Error downloading FFmpeg: {str(e)}")
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    download_ffmpeg()
