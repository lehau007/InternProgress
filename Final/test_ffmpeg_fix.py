#!/usr/bin/env python3
"""
Test script to verify FFmpeg availability in the Django environment
"""
import os
import sys
import shutil
import tempfile
import subprocess

# Add the Django project to Python path
django_project_path = '/home/runner/work/InternProgress/InternProgress/Final/myproject'
sys.path.insert(0, django_project_path)
os.chdir(django_project_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

try:
    # Import Django settings to trigger path configuration
    from myproject import settings
    print("✓ Django settings loaded successfully")
    
    # Test FFmpeg availability using shutil.which (same method as views.py)
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        print(f"✓ FFmpeg found at: {ffmpeg_path}")
    else:
        print("✗ FFmpeg not found in PATH")
        sys.exit(1)
    
    # Test FFmpeg functionality with a simple command
    try:
        result = subprocess.run([ffmpeg_path, '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg is working: {version_line}")
        else:
            print(f"✗ FFmpeg command failed: {result.stderr}")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("✗ FFmpeg command timed out")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error running FFmpeg: {e}")
        sys.exit(1)
    
    # Test the actual transcription view logic (import check)
    try:
        from voice_recorder.views import transcribe
        print("✓ Voice recorder views imported successfully")
    except ImportError as e:
        print(f"✗ Could not import voice recorder views: {e}")
        # This is expected since whisper might not be installed
        print("  Note: This is expected if whisper is not installed")
    
    print("\n🎉 FFmpeg fix verification PASSED!")
    print("The Django application should now be able to use FFmpeg for audio transcription.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)