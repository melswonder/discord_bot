FROM python:3.13-slim

# OSレベルの依存関係（PROJなど）をインストール
# libproj-dev, proj-bin が pyproj のビルドに必要
RUN apt-get update && apt-get install -y \
    libproj-dev \
    proj-bin \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . .

# Botを実行
CMD ["python", "bot.py"]