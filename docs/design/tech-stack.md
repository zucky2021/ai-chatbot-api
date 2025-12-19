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

## MCP (Model Context Protocol)

### FastMCP

- [公式サイト](https://gofastmcp.com/)
- 選定理由
  - Model Context Protocol (MCP) サーバーを構築するためのPythonフレームワーク
  - Claude Desktop、VS Code等のAIクライアントからアクセス可能
  - 会話履歴の検索やAI機能の外部公開に活用
  - FastAPIとの統合が容易

- **MCP Python SDK（公式SDK）との比較**

| 観点                             | FastMCP | MCP Python SDK |
| -------------------------------- | :-----: | :------------: |
| 公式サポート                     |    ×    |       ○        |
| 高レベルAPI（デコレータベース）  |    ○    |       ×        |
| 高速プロトタイピング             |    ○    |       ×        |
| 低レベル制御                     |    ×    |       ○        |
| FastAPI統合                      |    ○    |       ×        |
| 学習コストの低さ                 |    ○    |       ×        |
| 長期メンテナンス安定性           |    ×    |       ○        |
| Pydanticによる自動バリデーション |    ○    |       ×        |
| 構造化出力の保証（自動リトライ） |    ○    |       ×        |
| LLMへのスキーマ情報公開          |    ○    |       ×        |
| 厳密モード選択                   |    ○    |       ×        |

- FastMCP選定の決め手
  - 開発体験（DX）を重視し、迅速な開発が可能
  - FastAPIとの統合が容易で、既存アーキテクチャにフィット
  - デコレータベースのシンプルなAPIで学習コストが低い
  - 本プロジェクトでは高レベルな抽象化で十分な要件
  - Pydanticモデルを活用した型安全なツール定義が可能

## インフラ・開発環境

### Docker & Docker Compose v2

- [公式サイト](https://www.docker.com/)
- 選定理由
  - 開発環境の統一と再現性の確保
  - マルチサービス（PostgreSQL、Redis、LocalStackなど）の一元管理
  - ローカル開発とプロダクション環境の整合性
  - コンテナベースのモダンな開発手法の学習
  - Docker Compose v2 でより効率的なサービス管理

### LocalStack

- [公式サイト](https://localstack.cloud/)
- 選定理由
  - AWSサービスのローカルエミュレーション
    - DynamoDB
    - ElastiCache
  - コスト削減と高速な開発サイクル
  - 実際のAWS環境に近い開発体験

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

## CI

### Husky

- [公式サイト](https://typicode.github.io/husky/)
- 選定理由
  - Gitフックの管理を簡素化
  - コミット前の自動チェック（リント、フォーマットなど）でコード品質を担保
  - 設定が簡単で、チーム全員が同じフックを実行可能
  - package.jsonと統合され、プロジェクト管理が容易

### GitHub Actions

- [公式サイト](https://docs.github.com/ja/actions)
- 選定理由
  - GitHubリポジトリと完全統合され、追加設定が不要
  - プルリクエストやコミット時に自動実行できる
  - 無料枠が充実しており、個人・小規模プロジェクトでも十分
  - YAML形式で直感的なワークフロー定義が可能
  - 豊富なアクション（actions）のエコシステム
  - 依存関係チェック、ビルド、テストなど様々なCI/CDタスクに対応
