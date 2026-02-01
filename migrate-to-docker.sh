#!/bin/bash
# 一键迁移脚本：从虚拟环境迁移到 Docker 容器

echo "=== NovaSR Docker 迁移脚本 ==="
echo ""

# 检查 Docker 和 NVIDIA 运行时
echo "[1/5] 检查 Docker 和 NVIDIA 支持..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "   安装命令: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! docker info | grep -q "nvidia"; then
    echo "⚠️  NVIDIA Docker 运行时未配置"
    echo "   安装 NVIDIA Container Toolkit:"
    echo "   https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    echo ""
    echo "   快速安装 (Ubuntu):"
    echo "   sudo apt-get install -y nvidia-container-toolkit"
    echo "   sudo nvidia-ctk runtime configure --runtime=docker"
    echo "   sudo systemctl restart docker"
    echo ""
fi

# 停止现有服务
echo "[2/5] 停止现有服务..."
pkill -f "api.py" 2>/dev/null || true
systemctl --user stop nova_sr 2>/dev/null || true

# 构建镜像
echo "[3/5] 构建 GPU Docker 镜像..."
cd /mnt/volume3/data/audio/tts_and_enhance/nova_sr/NovaSR
just build-gpu || docker build -f Dockerfile.gpu -t novasr-gpu:latest .

# 安装 systemd 服务
echo "[4/5] 安装 systemd 服务..."
sudo cp nova_sr_docker.service /etc/systemd/system/novasr-docker.service
sudo systemctl daemon-reload
sudo systemctl enable novasr-docker.service

# 启动服务
echo "[5/5] 启动 Docker 服务..."
sudo systemctl start novasr-docker.service
sleep 5

# 验证
echo ""
echo "=== 验证服务 ==="
if curl -s http://localhost:10999/health | grep -q "ok"; then
    echo "✅ 服务运行正常"
    echo ""
    echo "常用命令:"
    echo "  sudo systemctl status novasr-docker  # 查看状态"
    echo "  sudo systemctl stop novasr-docker    # 停止服务"
    echo "  sudo systemctl restart novasr-docker # 重启服务"
    echo "  docker logs -f novasr-gpu            # 查看日志"
else
    echo "❌ 服务启动失败，查看日志:"
    echo "   docker logs novasr-gpu"
    echo "   sudo journalctl -u novasr-docker -f"
fi
