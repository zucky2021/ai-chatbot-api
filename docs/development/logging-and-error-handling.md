# 構造化ログとエラーハンドリング

## 概要

AI Chatbot APIでは、構造化ログ（structlog）と統一されたエラーレスポンスを実装しています。
これにより、Amazon Athenaでのログ検索が容易になり、問題の特定と解決が効率化されます。

## 構造化ログ

### 基本概念

構造化ログでは、**独自のクラスやオブジェクトを定義するのではなく**、structlogの既存のログイベントに対して、キーワード引数でフィールドを動的に追加します。

```python
# ❌ 独自クラスの定義は不要
# class LogEvent:
#     event: str
#     user_id: str
#     ...

# ✅ structlogのロガーにキーワード引数で直接渡す
logger.info(
    "event_name",      # 第1引数: イベント名（eventフィールド）
    user_id=user_id,   # キーワード引数: 追加フィールド
    field2=value2      # キーワード引数: 追加フィールド
)
```

structlogが自動的にこれらをJSON形式のログイベントに変換します。

### 基本的な使い方

```python
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)

# INFO レベル
logger.info(
    "event_name",
    user_id=user_id,
    session_id=session_id,
    additional_data="value"
)

# WARNING レベル
logger.warning(
    "validation_error",
    field="email",
    error="Invalid format"
)

# ERROR レベル（スタックトレース付き）
logger.error(
    "database_error",
    error=str(e),
    query="SELECT ...",
    exc_info=True  # スタックトレースを含める
)

# DEBUG レベル
logger.debug(
    "cache_hit",
    key=cache_key,
    ttl=3600
)
```

### ログの特徴

1. **JSON形式で出力**
   - 本番環境（`JSON_LOGS=True`）: 機械可読なJSON形式
   - 開発環境（`JSON_LOGS=False`）: 人間が読みやすい形式

2. **自動的に含まれる情報**
   - タイムスタンプ（ISO 8601形式）
   - ログレベル
   - ロガー名
   - リクエストID（ミドルウェアで自動付与）
   - HTTPメソッド、パス、クライアントIP

3. **機密情報のマスキング**
   - APIキー、パスワード、トークン等は自動的に `***MASKED***` に置換
   - マスキング対象: `GOOGLE_AI_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `password`, `secret`, `token` など

### ログフィールド（プロパティ）一覧

構造化ログには以下のフィールドが含まれます。これらは**structlogが自動的に管理するログイベントのプロパティ**であり、独自のクラス定義は不要です。

#### 自動的に追加されるフィールド

| フィールド名  | 型     | 説明                                                | 設定元              |
| ------------- | ------ | --------------------------------------------------- | ------------------- |
| `timestamp`   | string | ISO 8601形式のタイムスタンプ                        | structlog           |
| `level`       | string | ログレベル（debug, info, warning, error, critical） | structlog           |
| `logger`      | string | ロガー名（モジュール名）                            | structlog           |
| `application` | string | アプリケーション名（固定値: "ai-chatbot-api"）      | logging.py          |
| `environment` | string | 環境名（例: "production", "development"）           | logging.py          |
| `request_id`  | string | リクエストID（UUID）                                | RequestIDMiddleware |
| `method`      | string | HTTPメソッド（GET, POST等）                         | RequestIDMiddleware |
| `path`        | string | リクエストパス（例: "/api/chat/messages"）          | RequestIDMiddleware |
| `client_ip`   | string | クライアントIPアドレス                              | RequestIDMiddleware |

#### 明示的に追加するフィールド

| フィールド名     | 型     | 説明                   | 例                     |
| ---------------- | ------ | ---------------------- | ---------------------- |
| `event`          | string | イベント名（第1引数）  | "send_message_started" |
| `user_id`        | string | ユーザーID             | "user123"              |
| `session_id`     | string | セッションID           | "session456"           |
| `error`          | string | エラーメッセージ       | "Connection timeout"   |
| `error_code`     | string | エラーコード           | "VALIDATION_ERROR"     |
| `duration_ms`    | number | 処理時間（ミリ秒）     | 123.45                 |
| `message_length` | number | メッセージ長           | 42                     |
| その他           | any    | 任意のコンテキスト情報 | -                      |

#### 例外発生時に追加されるフィールド（`exc_info=True` の場合）

| フィールド名 | 型     | 説明                             |
| ------------ | ------ | -------------------------------- |
| `exception`  | string | 例外のスタックトレース           |
| `error_type` | string | 例外クラス名（例: "ValueError"） |

### JSON形式の例

```json
{
  "event": "send_message_started",
  "user_id": "user123",
  "session_id": "session456",
  "message_length": 42,
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/chat/messages",
  "client_ip": "192.168.1.100",
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "info",
  "logger": "app.presentation.controllers.chat_controller",
  "application": "ai-chatbot-api",
  "environment": "production"
}
```

## エラーハンドリング

### AppErrorの使用

アプリケーション固有のエラーは `AppError` を使用します。

```python
from app.presentation.middleware.error_handler import AppError
from app.presentation.models.error import ErrorCode

# バリデーションエラー
raise AppError(
    error_code=ErrorCode.VALIDATION_ERROR,
    message="ユーザーIDは必須です",
    details={"field": "user_id"}
)

# セッションエラー
raise AppError(
    error_code=ErrorCode.INVALID_SESSION,
    message="セッションが見つかりません",
    details={"session_id": session_id}
)

# AIサービスエラー
raise AppError(
    error_code=ErrorCode.AI_SERVICE_ERROR,
    message="AI応答の生成に失敗しました",
    details={"model": "gemini-flash", "error": str(e)}
)
```

### エラーコード一覧

| エラーコード                | HTTPステータス | 説明                     |
| --------------------------- | -------------- | ------------------------ |
| `VALIDATION_ERROR`          | 400            | 入力値の検証エラー       |
| `NOT_FOUND`                 | 404            | リソースが見つからない   |
| `INVALID_SESSION`           | 400            | 無効なセッション         |
| `SESSION_EXPIRED`           | 401            | セッションの有効期限切れ |
| `AI_SERVICE_ERROR`          | 500            | AI サービスのエラー      |
| `AI_RESPONSE_TIMEOUT`       | 504            | AI応答タイムアウト       |
| `DATABASE_ERROR`            | 500            | データベースエラー       |
| `DATABASE_CONNECTION_ERROR` | 503            | データベース接続エラー   |
| `CACHE_ERROR`               | 500            | キャッシュエラー         |
| `UNAUTHORIZED`              | 401            | 認証エラー               |
| `FORBIDDEN`                 | 403            | 認可エラー               |
| `INTERNAL_ERROR`            | 500            | 内部エラー               |

### エラーレスポンスの形式

```json
{
  "error": {
    "code": "INVALID_SESSION",
    "message": "セッションが見つかりません",
    "details": {
      "session_id": "session456"
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## リクエストID

各リクエストに一意のIDが付与され、ログとレスポンスヘッダーに含まれます。

### レスポンスヘッダー

```sh
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

### クライアントからのリクエストID指定

クライアントが `X-Request-ID` ヘッダーを送信した場合、そのIDが使用されます。

```sh
curl -H "X-Request-ID: my-custom-request-id" http://localhost:8000/api/chat/messages
```

### エンドポイント内でのリクエストID取得

```python
from fastapi import Request

async def my_endpoint(request: Request):
    request_id = request.state.request_id
    # ...
```

## 環境変数設定

### .env ファイル

```env
# ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
LOG_LEVEL=INFO

# JSON形式でログ出力（本番: true、開発: false）
JSON_LOGS=true
```

### 開発環境

```env
LOG_LEVEL=DEBUG
JSON_LOGS=false
```

### 本番環境

```env
LOG_LEVEL=INFO
JSON_LOGS=true
```

## LangChainログの統合

LangChainの内部ログも自動的にstructlogに統合されます。

```python
# 設定は main.py で自動実行
from app.infrastructure.langchain_logging import configure_langchain_logging

configure_langchain_logging()
```

## Amazon Athenaでのログ検索

JSON形式のログはCloudWatch Logsに出力され、Athenaで検索可能です。

### CloudWatch vs LocalStack

#### 本番環境（AWS CloudWatch）

- **メリット**
  - フルマネージドサービス（運用不要）
  - Athenaとの統合が簡単
  - CloudWatch Insights による高度な検索
  - アラート、ダッシュボード等の機能が豊富
- **料金**
  - **無料枠**: 月5GBまで無料（新規アカウントで12ヶ月間）
  - 取り込み: $0.50/GB
  - 保存: $0.03/GB/月
  - 参考: [CloudWatch 料金](https://aws.amazon.com/jp/cloudwatch/pricing/)

#### 開発環境（LocalStack）

- **メリット**
  - 完全無料（ローカル実行）
  - ネットワーク不要
  - AWSアカウント不要
  - テスト・デバッグが容易
- **デメリット**
  - Athena機能は限定的（Pro版が必要）
  - 本番環境との完全な互換性は保証されない

#### 推奨構成

| 環境              | ログ出力先                          | 用途                   |
| ----------------- | ----------------------------------- | ---------------------- |
| ローカル開発      | 標準出力（`JSON_LOGS=false`）       | デバッグ、開発         |
| Docker開発        | 標準出力 → Docker Logs              | コンテナ環境でのテスト |
| ステージング/本番 | CloudWatch Logs（`JSON_LOGS=true`） | 運用、監視、分析       |

**結論**: ローカル開発では標準出力で十分。CloudWatchは本番・ステージング環境で使用することを推奨します。

### 検索例

```sql
-- 特定のリクエストIDのログを検索
SELECT *
FROM cloudwatch_logs
WHERE request_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY timestamp DESC;

-- エラーログのみを検索
SELECT *
FROM cloudwatch_logs
WHERE level = 'error'
  AND timestamp >= timestamp '2024-01-15 00:00:00'
ORDER BY timestamp DESC;

-- 特定のユーザーのアクティビティを検索
SELECT *
FROM cloudwatch_logs
WHERE user_id = 'user123'
  AND timestamp >= timestamp '2024-01-15 00:00:00'
ORDER BY timestamp DESC;

-- AI応答の生成時間を分析
SELECT
  AVG(CAST(json_extract_scalar(details, '$.duration') AS DOUBLE)) as avg_duration,
  COUNT(*) as count
FROM cloudwatch_logs
WHERE event = 'send_message_completed'
  AND timestamp >= timestamp '2024-01-15 00:00:00';
```

## ベストプラクティス

### ログ出力のタイミング

1. **処理の開始時**

   ```python
   logger.info("operation_started", user_id=user_id, operation="create_session")
   ```

2. **処理の完了時**

   ```python
   logger.info("operation_completed", user_id=user_id, session_id=session_id)
   ```

3. **エラー発生時**

   ```python
   logger.error("operation_failed", error=str(e), exc_info=True)
   ```

### イベント名の命名規則

- 小文字とアンダースコアを使用
- 動詞 + 名詞の形式（例: `send_message_started`, `create_session_completed`）
- エラーの場合は `_error` サフィックス（例: `database_error`）

### 構造化データの活用

```python
# ❌ 悪い例：文字列に情報を埋め込む
logger.info(f"User {user_id} created session {session_id}")

# ✅ 良い例：構造化データとして記録
logger.info(
    "session_created",
    user_id=user_id,
    session_id=session_id
)
```

### 機密情報の取り扱い

```python
# ❌ 悪い例：機密情報をログに出力
logger.info("api_call", api_key=settings.GOOGLE_AI_API_KEY)

# ✅ 良い例：機密情報は出力しない（自動マスキングされるが、そもそも避ける）
logger.info("api_call", model=settings.GOOGLE_AI_MODEL)
```

### パフォーマンス測定

```python
import time

start_time = time.time()
# 処理
duration = time.time() - start_time

logger.info(
    "operation_completed",
    operation="database_query",
    duration_ms=duration * 1000
)
```

## トラブルシューティング

### ログが出力されない

1. ログレベルを確認

   ```env
   LOG_LEVEL=DEBUG
   ```

2. ロガーが正しく取得されているか確認

   ```python
   from app.infrastructure.logging import get_logger
   logger = get_logger(__name__)  # ✅
   # logger = logging.getLogger(__name__)  # ❌
   ```

### JSON形式で出力されない

```env
JSON_LOGS=true
```

### リクエストIDがログに含まれない

ミドルウェアが正しく登録されているか確認（`main.py`）:

```python
app.add_middleware(RequestIDMiddleware)
```

## 参考

- [structlog Documentation](https://www.structlog.org/)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Amazon Athena](https://aws.amazon.com/jp/athena/)
