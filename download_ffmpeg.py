import os
import zipfile
import urllib.request
import shutil
import sys

def download_ffmpeg():
    """Download and install ffmpeg for Windows"""
    print("Downloading ffmpeg for Windows...")
    
    # Create a directory for ffmpeg
    os.makedirs("ffmpeg", exist_ok=True)
    
    # Download URL for ffmpeg (essentials build)
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = "ffmpeg/ffmpeg.zip"
    
    # Download the zip file
    print(f"Downloading from {url}...")
    try:
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        print(f"Error downloading ffmpeg: {e}")
        return False
    
    # Extract the zip file
    print("Extracting zip file...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg")
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        return False
    
    # Find the bin directory
    bin_dir = None
    for root, dirs, files in os.walk("ffmpeg"):
        if "bin" in dirs:
            bin_dir = os.path.join(root, "bin")
            break
    
    if not bin_dir:
        print("Could not find bin directory in extracted files")
        return False
    
    # Copy ffmpeg.exe to the current directory
    print("Copying ffmpeg.exe to current directory...")
    try:
        shutil.copy(os.path.join(bin_dir, "ffmpeg.exe"), "ffmpeg.exe")
    except Exception as e:
        print(f"Error copying ffmpeg.exe: {e}")
        return False
    
    # Clean up
    print("Cleaning up...")
    try:
        shutil.rmtree("ffmpeg")
    except Exception as e:
        print(f"Error cleaning up: {e}")
    
    print("ffmpeg installed successfully!")
    return True

if __name__ == "__main__":
    download_ffmpeg()
