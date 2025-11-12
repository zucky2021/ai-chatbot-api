# バックエンドパッケージ

## 設定ファイル

- [pyproject.toml](./../../../backend/pyproject.toml)

## パッケージ管理

### 更新確認

- 更新可能なパッケージを確認するには:

```sh
uv pip list --outdated
```

- `pyproject.toml`の依存関係を更新した場合に`uv.lock`がどのように変更されるかを確認するには:

```sh
uv lock --upgrade --dry-run
```

### セキュリティ脆弱性の確認

- 依存関係のセキュリティ脆弱性をスキャンするには：

```sh
uv run pip-audit --desc
```

### 実際に更新する場合

#### 方法1: pyproject.tomlを更新してからロックファイルを更新（推奨）

1. `uv pip list --outdated`で更新可能なパッケージを確認
2. `pyproject.toml`でバージョンを更新（例: `boto3==1.40.70` → `boto3==1.40.71`）
3. 以下のコマンドで`uv.lock`を更新：

   ```sh
   uv lock --upgrade
   ```

4. 依存関係を再インストール：

   ```sh
   uv sync
   ```

## パッケージ説明

### 本番依存関係（dependencies）

#### Webフレームワーク・サーバー

- **fastapi**: 高速なAPIフレームワーク。型ヒントと自動ドキュメント生成に対応
- **uvicorn[standard]**: ASGIサーバー。FastAPIの実行に使用
- **websockets**: WebSocket通信の実装

#### データベース関連

- **sqlalchemy**: ORM。データベース操作を抽象化
- **alembic**: SQLAlchemy用のマイグレーションツール
- **psycopg2-binary**: PostgreSQL用のアダプタ（バイナリ版）
- **asyncpg**: PostgreSQL用の非同期ドライバ
- **greenlet**: 軽量なコルーチンライブラリ（SQLAlchemyの非同期処理で使用）

#### キャッシュ・ストレージ

- **redis**: Redisクライアント
- **hiredis**: Redis用の高速パーサー（C拡張）

#### AWS関連

- **boto3**: AWS SDK for Python（DynamoDB、S3など）

#### ユーティリティ

- **python-multipart**: マルチパートフォームデータの解析（FastAPIでファイルアップロードなど）
- **python-dotenv**: `.env` からの環境変数読み込み
- **pydantic**: データバリデーションとシリアライゼーション
- **pydantic-settings**: Pydanticベースの設定管理

#### LangChain関連

- **langchain**: LLMアプリケーション構築フレームワーク
- **langchain-core**: LangChainのコア機能
- **langchain-community**: コミュニティ提供の統合・ツール
- **langchain-google-genai**: Google Gemini API統合
- **langgraph**: LangChain上でステートフルなワークフローを構築

### 開発依存関係（dev）

- **mypy**: 静的型チェッカー
- **ruff**: 高速なリンター・フォーマッター
- **pytest**: テストフレームワーク
- **pip-audit**: 依存関係の脆弱性スキャン
