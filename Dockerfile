# 使用Python 3.9作为基础镜像
FROM python:3.10.13-slim

# 设置工作目录
WORKDIR /app

COPY resources/debian.sources /etc/apt/sources.list.d/debian.sources

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CUDA_VISIBLE_DEVICES=0 \
    PYTHONPATH=/app \
    HF_ENDPOINT=https://hf-mirror.com

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app/

# 安装Python依赖
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 创建临时目录
RUN mkdir -p /app/temp

# 暴露端口
EXPOSE 8080

# 启动OCR API服务
CMD ["python", "ocr_api.py"]