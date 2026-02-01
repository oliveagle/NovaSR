#!/usr/bin/env sh
cd /mnt/volume3/data/audio/tts_and_enhance/nova_sr/NovaSR
export PYTHONPATH=/mnt/volume3/data/audio/tts_and_enhance/nova_sr/NovaSR
export OMP_NUM_THREADS=4
export PYTHONUNBUFFERED=1

trap 'kill -TERM $PID' TERM
/home/oliveagle/venvs/comfyui_nvidia/bin/python -u api.py >> /home/oliveagle/data/log/nova_sr.log 2>&1 &
PID=$!
wait $PID
trap - TERM
