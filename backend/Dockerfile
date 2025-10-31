FROM python:3.11-slim

# Cài đặt các dependencies hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Giảm warning + tăng tốc cài package
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# Copy requirements và cài đặt Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
# Tải sẵn model CLIP vào cache để không phải tải lại mỗi lần container restart
RUN python -c "import clip; clip.load('ViT-B/32', device='cpu')"

# Copy toàn bộ backend code
COPY . .

# Create uploads directory and set permissions
RUN mkdir -p uploads && chown -R root:root uploads && chmod -R 777 uploads

# Expose port
EXPOSE 8000

# Command để chạy ứng dụng
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
