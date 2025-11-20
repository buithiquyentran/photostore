FROM python:3.11-slim

# Cài đặt các dependencies hệ thống cần thiết
# Sử dụng cache mount cho apt để tăng tốc độ cài đặt lại
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Giảm warning + tăng tốc cài package
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Cho phép pip cache để tăng tốc độ build lần sau
ENV PIP_NO_CACHE_DIR=0
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements và cài đặt Python packages
COPY requirements.txt .

# Sử dụng cache mount cho pip để không phải download lại wheel
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Tải sẵn model CLIP vào cache để không phải tải lại mỗi lần container restart
# Lưu ý: Model sẽ được lưu vào layer của image
RUN python -c "import clip; clip.load('ViT-B/32', device='cpu')"

# Copy toàn bộ backend code
COPY . .

# Create uploads directory and set permissions
RUN mkdir -p uploads && chown -R root:root uploads && chmod -R 777 uploads

# Expose port
EXPOSE 8000

# Command để chạy ứng dụng
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
