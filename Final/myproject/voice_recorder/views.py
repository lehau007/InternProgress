import os
import tempfile
import whisper
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# ...existing code...
import shutil
import mimetypes
# ...existing code...

model = whisper.load_model("base")

def index(request):
    return render(request, 'voice_recorder/index.html')

@csrf_exempt
def transcribe(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        # Check ffmpeg availability early for clearer errors
        if shutil.which('ffmpeg') is None:
            return JsonResponse({"success": False, "error": "FFmpeg not found. Install FFmpeg and ensure it is on PATH."})

        audio_file = request.FILES['audio']
        # Preserve the original extension (important for decoding)
        ext = os.path.splitext(audio_file.name)[1].lower()
        if not ext:
            ext = mimetypes.guess_extension(getattr(audio_file, "content_type", "") or "") or ".webm"

        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                for chunk in audio_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            if tmp_file_path and os.path.exists(tmp_file_path):
                result = model.transcribe(tmp_file_path)
                transcription = result.get("text", "")
                return JsonResponse({"success": True, "transcription": transcription})
            else:
                return JsonResponse({"success": False, "error": "Failed to create temporary file"})
        except FileNotFoundError as e:
            # Common when ffmpeg is missing
            return JsonResponse({"success": False, "error": f"{e}. Ensure FFmpeg is installed and on PATH."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except OSError:
                    pass

    return JsonResponse({"success": False, "error": "Invalid request"})