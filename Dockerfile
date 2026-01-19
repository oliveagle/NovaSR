FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsox-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir -e .

CMD ["python", "-c", "from NovaSR import FastSR; print('NovaSR Docker 环境已就绪 (CPU模式)'); print('使用示例: upsampler = FastSR(device=\\'cpu\\')')"]
