import os
#os.environ['CUDA_VISIBLE_DEVICES'] = ''
#os.environ['HIP_VISIBLE_DEVICES'] = ''

from NovaSR import FastSR
from IPython.display import Audio, display
import torch
from pathlib import Path

# ckpt_path = "/home/oliveagle/.cache/huggingface/hub/models--YatharthS--NovaSR/snapshots/08532ca96dad8d73975e2d110d76e0831255bdbf/pytorch_model_v1.bin"

#if os.path.exists(ckpt_path):
#    upsampler = FastSR(ckpt_path=ckpt_path, half=False)
#else:
#    upsampler = FastSR(half=False)

upsampler = FastSR(half=False)


input_path = 'audio_1_11k.mp3'
lowres_audio = upsampler.load_audio(input_path)

highres_audio = upsampler.infer(lowres_audio).cpu()

display(Audio(highres_audio, rate=48000))

output_path = f"{Path(input_path).stem}_novasr_48k_cpu.wav"
import soundfile as sf
highres_numpy = highres_audio.squeeze(0).numpy()
sf.write(output_path, highres_numpy, 48000)
print(f"Audio saved to {output_path}")
