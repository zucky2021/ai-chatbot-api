# 技術スタック

## バックエンド

### FastAPI

- [公式サイト](https://fastapi.tiangolo.com/ja/)
- 選定理由
  - モダンで高速なWebフレームワーク
  - 自動APIドキュメント生成機能
  - Pydanticによる型安全性
  - WebSocket対応

### WebSocket

- [参考サイト - MDN](https://developer.mozilla.org/ja/docs/Web/API/WebSocket)
- 選定理由
  - リアルタイムチャットには必須の双方向通信
  - サーバーサイドイベント（SSE）よりも柔軟
  - AIからのストリーミング応答に対応
  - 低遅延での通信が可能

## データベース

### PostgreSQL

- [公式サイト](https://www.postgresql.org/)
- 選定理由
  - リレーショナルデータベースとして会話履歴を保存
  - pgvector拡張によるベクトル検索機能
  - ACIDトランザクションでデータ整合性を保証
  - Docker環境での運用が容易

### DynamoDB

- [公式サイト](https://aws.amazon.com/jp/dynamodb/)
- 選定理由
  - AWSのNoSQLデータベースを学習
  - ユーザーセッション、設定などスキーマレスなデータ保存に適している
  - LocalStackによりAWS環境をローカルで再現
  - コスト削減と学習効率向上

### ElastiCache

- [公式サイト](https://aws.amazon.com/jp/elasticache/redis/)
- 選定理由
  - インメモリキャッシュによる高速なデータアクセス
  - セッション管理やレート制限などに活用

## フロントエンド

### Vite

- [公式サイト](https://ja.vite.dev/)
- 選定理由
  - 高速なビルドツールで開発体験が優れている

### React + TypeScript

- [公式サイト](https://ja.react.dev/)
- 選定理由
  - React: コンポーネントベースのUI構築
  - TypeScript: 型安全性による開発効率向上

### pnpm

- [公式サイト](https://pnpm.io/ja/)
- 選定理由
  - npm/yarnよりも高速なインストール
  - ディスク効率が良い（node_modulesの重複削減）
  - 厳密なパッケージ依存関係管理

## 開発ツール

### uv（Python）

- [公式サイト](https://docs.astral.sh/uv/)
- 選定理由
  - pipの10-100倍の高速なインストール
  - Rust実装による高いパフォーマンス
  - プロジェクト依存関係の効率的な管理

### pipx

- [参考 - GitHub](https://github.com/pypa/pipx)
- 選定理由
  - CLIツールのグローバルインストールに使用
  - 仮想環境を自動管理
  - システムのPython環境を汚染しない
