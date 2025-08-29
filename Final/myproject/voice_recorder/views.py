import os
import tempfile
import whisper
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import speech_recognition as sr
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

model = whisper.load_model("base")

def index(request):
    return render(request, 'voice_recorder/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def transcribe(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        
        # Check Wav file
        content_type = audio_file.content_type
        file_name = audio_file.name or ''
        
        if content_type not in ['audio/wav', 'audio/wave', 'audio/x-wav'] and not file_name.lower().endswith('.wav'):
            return JsonResponse({
                'success': False,
                'error': 'Please upload a WAV file. Other formats require FFmpeg installation.',
                'received_type': content_type,
                'received_name': file_name
            }, status=400)
        
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                wav_temp_path = temp_file.name
            
            # Initialize speech recognizer
            recognizer = sr.Recognizer()
            
            # Load the WAV file
            with sr.AudioFile(wav_temp_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
            
            # Transcribe using Vietnamese language
            transcribed_text = recognizer.recognize_google(audio_data, language='vi-VN')
            
            # Clean up
            os.unlink(wav_temp_path)
            
            return JsonResponse({
                'success': True,
                'transcription': transcribed_text.strip(),
                'method': 'Google Web Speech API (Vietnamese)'
            })
            
        except sr.UnknownValueError:
            return JsonResponse({
                'success': False,
                'error': 'Could not understand the audio'
            }, status=400)
        except Exception as e:
            try:
                if 'wav_temp_path' in locals():
                    os.unlink(wav_temp_path)
            except:
                pass
            
            return JsonResponse({
                'success': False,
                'error': f'Transcription failed: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'No audio file provided'
    }, status=400)