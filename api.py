import io
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import numpy as np

from NovaSR import FastSR

app = FastAPI()

upsampler = FastSR(
    half=False,
    device='cpu',
)

@app.post("/upsample")
async def upsample_audio(file: UploadFile = File(...)):
    """
    Upload an audio file and receive upsampled 48kHz audio.
    Returns: WAV audio at 48kHz (in-memory, no file storage)
    """
    if file.content_type and not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="Must be an audio file")

    contents = await file.read()

    try:
        import librosa
        audio, sample_rate = librosa.load(
            io.BytesIO(contents),
            sr=None,
            mono=True
        )
        audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
        lowres_wav = torch.from_numpy(audio).float().unsqueeze(0).unsqueeze(1)

        with torch.no_grad():
            highres_audio = upsampler.model(lowres_wav).squeeze(0).cpu()

        highres_numpy = highres_audio.numpy()

        buffer = io.BytesIO()
        import wave
        import struct

        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(48000)
            audio_int16 = (highres_numpy * 32767).astype('<i2')
            wav_file.writeframes(audio_int16.tobytes())
        buffer.seek(0)

        return StreamingResponse(
            iter([buffer.read()]),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="upsampled_48k.wav"',
                "Content-Length": str(buffer.tell()),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10999)
