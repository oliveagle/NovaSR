import io
import sys
import os
import struct
import torch
import torchaudio
import numpy as np
from scipy import signal
from aiohttp import web

from NovaSR import FastSR

LOG_FILE = "/home/oliveagle/data/log/nova_sr.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
        f.flush()

log("======== Loading model ========")

# Use local model path
MODEL_PATH = os.environ.get("MODEL_PATH", "/home/oliveagle/.cache/huggingface/hub/models--YatharthS--NovaSR/snapshots/08532ca96dad8d73975e2d110d76e0831255bdbf/pytorch_model_v1.bin")

log(f"======== Model path: {MODEL_PATH} ========")

upsampler = FastSR(
    ckpt_path=MODEL_PATH,
    half=False,
)

log("======== Model loaded ========")

async def health(request):
    return web.json_response({"status": "ok"})

async def upsample_audio(request):
    try:
        data = await request.post()
        file = data.get('file')
        
        if not file:
            return web.json_response({"detail": "No file uploaded"}, status=400)
        
        content_type = file.content_type or ""
        if not content_type.startswith('audio/'):
            return web.json_response({"detail": "Must be an audio file"}, status=400)
        
        contents = file.file.read()
        
        # Check if WAV file (starts with RIFF)
        if contents[:4] == b'RIFF':
            import wave
            import tempfile
            import soundfile as sf
            # Save to temp file and load with torchaudio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            
            try:
                audio, sample_rate = torchaudio.load(tmp_path)
                audio = audio[:1, :]  # Take first channel (mono)
                os.unlink(tmp_path)
            except Exception as e:
                os.unlink(tmp_path)
                raise e
        else:
            # Use soundfile for other formats (MP3, etc.)
            import soundfile as sf
            audio, sample_rate = sf.read(io.BytesIO(contents))
            # Ensure mono
            if audio.ndim > 1:
                audio = audio[:, 0] if audio.shape[1] == 2 else audio.mean(axis=1)
            audio = torch.from_numpy(audio).float().unsqueeze(0)
        
        # Resample to 16kHz using torchaudio kaiser_window (like GPU version)
        audio_16k = torchaudio.functional.resample(audio, sample_rate, 16000, resampling_method="kaiser_window")
        
        lowres_wav = audio_16k.unsqueeze(1).to(upsampler.device)

        with torch.no_grad():
            highres_audio = upsampler.model(lowres_wav).squeeze(0).cpu()

        highres_numpy = highres_audio.numpy()

        buffer = io.BytesIO()
        import wave

        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(48000)
            audio_int16 = (highres_numpy * 32767).astype('<i2')
            wav_file.writeframes(audio_int16.tobytes())
        buffer.seek(0)

        return web.Response(
            body=buffer.read(),
            content_type="audio/wav",
            headers={
                "Content-Disposition": 'attachment; filename="upsampled_48k.wav"',
                "Content-Length": str(buffer.tell()),
            }
        )
    except Exception as e:
        log(f"Error: {e}")
        return web.json_response({"detail": str(e)}, status=500)

app = web.Application(client_max_size=100*1024*1024)  # 100MB
app.router.add_get('/health', health)
app.router.add_post('/upsample', upsample_audio)

if __name__ == "__main__":
    log("======== Starting server on http://0.0.0.0:10999 ========")
    web.run_app(app, host="0.0.0.0", port=10999, print=None)
