# ==============================================================================
# ベースステージ: 共通のセットアップ
# ==============================================================================
FROM python:3.12-slim AS base

# システム依存関係のインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 非ルートユーザーの作成（セキュリティ強化）
RUN groupadd -r appuser && \
    useradd -r -g appuser -m -d /home/appuser appuser && \
    mkdir -p /home/appuser/.cache/uv && \
    chown -R appuser:appuser /home/appuser

# 作業ディレクトリを設定
WORKDIR /app

# uvをインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# 依存関係ファイルをコピー（レイヤーキャッシュの最適化）
COPY pyproject.toml uv.lock* ./

# ==============================================================================
# 開発ステージ: 開発環境用
# ==============================================================================
FROM base AS dev

# 開発依存関係も含めてインストール
RUN uv sync --frozen && \
    rm -rf /root/.cache

# アプリケーションコードをコピー（開発時はボリュームマウントで上書きされる）
COPY . .

# ファイルの所有権を非ルートユーザーに変更（セキュリティ強化）
RUN chown -R appuser:appuser /app

# 非ルートユーザーに切り替え（セキュリティ強化）
USER appuser

# ポート8000を公開
EXPOSE 8000

# 開発用のデフォルトコマンド（ホットリロード有効）
CMD ["uv", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# ==============================================================================
# 本番ステージ: 本番環境用
# ==============================================================================
FROM base AS prod

# 本番依存関係のみインストール（開発依存関係は除外）
RUN uv sync --frozen --no-dev && \
    rm -rf /root/.cache

# アプリケーションコードをコピー
COPY . .

# ファイルの所有権を非ルートユーザーに変更（セキュリティ強化）
RUN chown -R appuser:appuser /app

# 非ルートユーザーに切り替え（セキュリティ強化）
USER appuser

# ポート8000を公開
EXPOSE 8000

# ヘルスチェックを追加（本番環境で重要）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# 本番用のデフォルトコマンド
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
