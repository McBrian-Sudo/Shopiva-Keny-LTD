import os
import tempfile

from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .ai import _catalog, _fallback, shop_assistant


def transcribe_voice(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    if not os.getenv("OPENAI_API_KEY", "").strip():
        return JsonResponse({"ok": False, "error": "Voice AI is not configured yet."}, status=503)

    audio = request.FILES.get("audio")
    if not audio:
        return JsonResponse({"ok": False, "error": "No voice recording was received."}, status=400)

    if audio.size > 10 * 1024 * 1024:
        return JsonResponse({"ok": False, "error": "Voice recording is too large. Please keep it under 10 MB."}, status=400)

    suffix = ".webm"
    name = (audio.name or "").lower()
    if "." in name:
        suffix = "." + name.rsplit(".", 1)[-1][:8]

    try:
        from openai import OpenAI

        with tempfile.NamedTemporaryFile(suffix=suffix) as temp:
            for chunk in audio.chunks():
                temp.write(chunk)
            temp.flush()
            with open(temp.name, "rb") as voice_file:
                transcript = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).audio.transcriptions.create(
                    model=os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe"),
                    file=voice_file,
                )

        return JsonResponse({"ok": True, "text": getattr(transcript, "text", "").strip()})
    except Exception:
        return JsonResponse({"ok": False, "error": "I could not understand that recording. Please try again."}, status=502)


def speak_text(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    if not os.getenv("OPENAI_API_KEY", "").strip():
        return JsonResponse({"ok": False, "error": "Voice AI is not configured yet."}, status=503)

    text = request.POST.get("text", "").strip()
    if not text:
        return JsonResponse({"ok": False, "error": "No text was supplied."}, status=400)

    # Keep spoken responses concise and prevent accidental huge audio requests.
    text = text[:2500]

    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
            output_path = temp.name

        try:
            speech = client.audio.speech.create(
                model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
                voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
                input=text,
                response_format="mp3",
            )
            speech.write_to_file(output_path)
            return FileResponse(
                open(output_path, "rb"),
                as_attachment=False,
                filename="shopiva-ai.mp3",
                content_type="audio/mpeg",
            )
        finally:
            # FileResponse owns the open file after return; avoid deleting it
            # here because some WSGI servers read it lazily.
            pass
    except Exception:
        return JsonResponse({"ok": False, "error": "Voice feedback is temporarily unavailable."}, status=502)
