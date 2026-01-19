FROM python:3.12-slim

# OSレベルの依存関係をインストール
# g++ を追加しました
RUN apt-get update && apt-get install -y \
    libproj-dev \
    proj-bin \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Botを実行
CMD ["python", "bot.py"]