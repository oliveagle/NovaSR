default:
    @echo "Usage: just <recipe>"
    @echo ""
    @echo "GPU (NVIDIA Container) - 推荐用于生产环境:"
    @echo "  build-gpu     - Build GPU Docker image (nvidia pytorch base)"
    @echo "  run-gpu       - Run GPU container (port 10999)"
    @echo "  stop-gpu      - Stop GPU container"
    @echo "  logs-gpu      - View GPU container logs"
    @echo ""
    @echo "CPU (Podman) - 用于无 GPU 环境:"
    @echo "  build-cpu     - Build CPU Podman image"
    @echo "  run-cpu       - Run CPU container"
    @echo "  clean-cpu     - Remove CPU image"
    @echo ""
    @echo "Docker Compose:"
    @echo "  up            - Start GPU service with docker-compose"
    @echo "  down          - Stop all services"
    @echo "  ps            - Show running containers"

# GPU (NVIDIA Docker) - 推荐方案
build-gpu:
    docker build -f Dockerfile.gpu -t novasr-gpu:latest .

run-gpu:
    docker run -d --name novasr-gpu \
        --runtime=nvidia \
        --gpus all \
        -p 10999:10999 \
        -v /home/oliveagle/.cache/huggingface:/root/.cache/huggingface:ro \
        -v /home/oliveagle/data/log:/app/logs \
        -e USE_GPU=true \
        -e FP16_HALF=true \
        -e MODEL_PATH=/home/oliveagle/.cache/huggingface/hub/models--YatharthS--NovaSR/snapshots/08532ca96dad8d73975e2d110d76e0831255bdbf/pytorch_model_v1.bin \
        --restart unless-stopped \
        novasr-gpu:latest

stop-gpu:
    docker stop novasr-gpu && docker rm novasr-gpu

logs-gpu:
    docker logs -f novasr-gpu

# CPU (Podman) - 备用方案
build-cpu:
    podman build -t novasr-cpu:latest .

run-cpu:
    podman run -d --name novasr-cpu \
        -p 10998:10999 \
        -v /home/oliveagle/.cache/huggingface:/root/.cache/huggingface:ro \
        -v /home/oliveagle/data/log:/app/logs \
        -e USE_GPU=false \
        -e FP16_HALF=false \
        novasr-cpu:latest

clean-cpu:
    podman rmi novasr-cpu:latest

# Docker Compose 方案 (推荐用于统一管理)
up:
    docker-compose up -d novasr-gpu

down:
    docker-compose down

ps:
    docker-compose ps
