#!/usr/bin/env python3
"""
Setup script for the Django Voice Recorder application.
This script automatically sets up FFmpeg using imageio-ffmpeg.
"""
import os
import sys
import shutil
import subprocess

def setup_ffmpeg():
    """Set up FFmpeg binary in the expected location."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(project_dir, "myproject", "ffmpeg", "bin")
    ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg")
    
    if os.path.exists(ffmpeg_exe):
        print(f"✓ FFmpeg already exists at: {ffmpeg_exe}")
        return True
    
    try:
        # Create directory
        os.makedirs(ffmpeg_dir, exist_ok=True)
        print(f"Created directory: {ffmpeg_dir}")
        
        # Try to get FFmpeg from imageio-ffmpeg
        try:
            import imageio_ffmpeg
            source_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            shutil.copy2(source_ffmpeg, ffmpeg_exe)
            print(f"✓ FFmpeg copied from imageio-ffmpeg to: {ffmpeg_exe}")
            return True
        except ImportError:
            print("✗ imageio-ffmpeg not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "imageio-ffmpeg"])
            import imageio_ffmpeg
            source_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            shutil.copy2(source_ffmpeg, ffmpeg_exe)
            print(f"✓ FFmpeg installed and copied to: {ffmpeg_exe}")
            return True
            
    except Exception as e:
        print(f"✗ Error setting up FFmpeg: {e}")
        return False

def install_requirements():
    """Install Python requirements."""
    requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if os.path.exists(requirements_file):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
            print("✓ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Error installing requirements: {e}")
            return False
    else:
        print("No requirements.txt found, skipping...")
        return True

def main():
    """Main setup function."""
    print("Setting up Django Voice Recorder application...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("Setup failed during requirements installation")
        sys.exit(1)
    
    # Set up FFmpeg
    if not setup_ffmpeg():
        print("Setup failed during FFmpeg setup")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. cd myproject")
    print("2. python manage.py runserver")
    print("\nThe voice transcription should now work without FFmpeg errors.")

if __name__ == "__main__":
    main()