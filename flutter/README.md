# AI Chatbot Flutter App

Flutter製のAIチャットボットアプリケーションです。

## 概要

このアプリケーションは、バックエンドのFastAPI + LangChain/LangGraphと連携して、AIチャット機能を提供します。

## 機能

- リアルタイムチャット（WebSocket）
- ストリーミング応答
- Markdown表示
- ダークモード対応
- クロスプラットフォーム（iOS、Android、Web）

## セットアップ

### 前提条件

- Flutter SDK 3.0.0以上
- Dart SDK 3.0.0以上

### インストール

```bash
# 依存関係のインストール
flutter pub get

# 環境変数の設定
cp env.example .env
# .env を編集してAPIのURLを設定
```

### 開発

```bash
# iOS
flutter run -d ios

# Android
flutter run -d android

# Web
flutter run -d chrome

# すべてのデバイスを確認
flutter devices
```

### ビルド

```bash
# iOS
flutter build ios

# Android
flutter build apk
flutter build appbundle

# Web
flutter build web
```

## プロジェクト構成

```text
flutter/
├── lib/
│   ├── main.dart           # エントリーポイント
│   ├── models/             # データモデル
│   │   ├── message.dart
│   │   └── session.dart
│   ├── screens/            # 画面
│   │   └── chat_screen.dart
│   ├── services/           # サービス
│   │   ├── api_service.dart
│   │   └── websocket_service.dart
│   └── widgets/            # ウィジェット
│       ├── chat_input.dart
│       └── message_bubble.dart
├── test/                   # テスト
├── assets/                 # アセット
├── pubspec.yaml            # 依存関係
└── analysis_options.yaml   # Linter設定
```

## 技術スタック

| 項目           | 技術                  |
| -------------- | --------------------- |
| フレームワーク | Flutter 3.x           |
| 言語           | Dart 3.x              |
| 状態管理       | Riverpod              |
| HTTP           | http パッケージ       |
| WebSocket      | web_socket_channel    |
| Markdown       | flutter_markdown_plus |

## バックエンドとの連携

このアプリはバックエンドAPI（FastAPI）と以下のエンドポイントで連携します：

| エンドポイント                 | 説明              |
| ------------------------------ | ----------------- |
| `POST /api/chat/sessions`      | セッション作成    |
| `GET /api/chat/sessions/{id}`  | セッション取得    |
| `WS /api/chat/ws/{session_id}` | WebSocketチャット |

## 環境変数

| 変数           | 説明                 | デフォルト              |
| -------------- | -------------------- | ----------------------- |
| `API_BASE_URL` | APIのベースURL       | `http://localhost:8000` |
| `WS_BASE_URL`  | WebSocketのベースURL | `ws://localhost:8000`   |

## 開発ガイドライン

### コード規約

- `analysis_options.yaml`のlintルールに従う
- `flutter analyze`でエラーがないことを確認

### テスト

```bash
# ユニットテスト
flutter test

# 特定のテスト
flutter test test/models/message_test.dart
```

## トラブルシューティング

### WebSocket接続エラー

1. バックエンドが起動していることを確認
2. `.env`のURLが正しいことを確認
3. CORS設定を確認

### iOSシミュレーターでの接続

`localhost`ではなく`127.0.0.1`を使用するか、実際のIPアドレスを設定してください。

## 参考

- [Flutter公式ドキュメント](https://flutter.dev/docs)
- [Riverpod](https://riverpod.dev/)
- [バックエンドAPI](../backend/README.md)
