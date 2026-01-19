# モノレポ設計

## 概要

本プロジェクトでは、複数の技術スタック（Python、TypeScript、Dart）を**モノレポ（Monorepo）** 構成で管理しています。

## リポジトリ構成

```text
ai-chatbot-api/
├── backend/          # Python (FastAPI)
├── frontend/         # TypeScript (React + Vite)
├── flutter/          # Dart (Flutter)
├── lambda/           # Python (AWS CDK + Lambda)
├── localstack/       # Shell (ローカルAWS環境)
└── docs/             # ドキュメント
```

## 選定理由

### モノレポを選択した理由

| 観点                     | 判断          | 理由                                       |
| ------------------------ | ------------- | ------------------------------------------ |
| **プロジェクトの関連性** | ✅ 高い       | 同一のチャットボットアプリケーションを構成 |
| **開発チーム**           | ✅ 同一       | 個人開発（学習目的）                       |
| **リリースサイクル**     | ✅ 統一的     | 同時にデプロイ可能                         |
| **セキュリティ要件**     | ✅ 同一       | 特別な分離要件なし                         |
| **リポジトリサイズ**     | ✅ 小〜中規模 | 巨大なバイナリなし                         |
| **目的**                 | ✅ 学習・実験 | シンプルな構成が望ましい                   |

### 比較検討した選択肢

#### 1. モノレポ（直接追加）✅ 採用

```text
ai-chatbot-api/
├── backend/
├── frontend/
├── flutter/      # 直接追加
└── ...
```

| メリット                     | デメリット                    |
| ---------------------------- | ----------------------------- |
| 単一リポジトリで管理が簡単   | リポジトリサイズが増加        |
| 共通設定・ドキュメントを統一 | 言語ごとのツールが混在        |
| 関連する変更を1コミットで    | CI/CDの設定が複雑になる可能性 |
| 学習コストが最小             | -                             |

#### 2. Git Submodule ❌ 不採用

```text
ai-chatbot-api/
├── flutter/      # ← 別リポジトリへの参照
└── .gitmodules
```

| メリット                 | デメリット                           |
| ------------------------ | ------------------------------------ |
| リポジトリの独立性が高い | 操作が複雑（学習コスト高）           |
| 特定バージョンを固定可能 | `--recursive`を忘れると不完全なclone |
| 権限を分けられる         | detached HEAD問題が発生しやすい      |

**不採用理由**: 個人開発では複雑さに見合うメリットがない

#### 3. Git Subtree ❌ 不採用

```text
ai-chatbot-api/
├── flutter/      # ← コードがコピーされている
└── (履歴が統合)
```

| メリット                 | デメリット           |
| ------------------------ | -------------------- |
| 通常のcloneでOK          | 双方向同期が面倒     |
| サブモジュールより直感的 | 履歴が混在する可能性 |

**不採用理由**: 別リポジトリを維持する必要がなく、オーバーヘッド

#### 4. 完全に独立したリポジトリ ❌ 不採用

```text
github.com/user/ai-chatbot-api
github.com/user/ai-chatbot-flutter
```

| メリット       | デメリット         |
| -------------- | ------------------ |
| 最もシンプル   | 関連する変更が分散 |
| 自由に実験可能 | 共通設定の重複     |

**不採用理由**: 同一アプリケーションのため統一管理が望ましい

## モノレポの運用方針

### ディレクトリごとの独立性

各ディレクトリは独立した依存関係管理を持ちます：

| ディレクトリ | 言語       | 依存管理              |
| ------------ | ---------- | --------------------- |
| `backend/`   | Python     | `pyproject.toml` (uv) |
| `frontend/`  | TypeScript | `package.json` (pnpm) |
| `flutter/`   | Dart       | `pubspec.yaml` (pub)  |
| `lambda/`    | Python     | `pyproject.toml` (uv) |

### CI/CD の分離

GitHub Actions でパスフィルターを使用し、変更があった部分のみビルド：

```yaml
# .github/workflows/backend.yml
on:
  push:
    paths:
      - 'backend/**'

# .github/workflows/flutter.yml
on:
  push:
    paths:
      - 'flutter/**'
```

### 開発環境

開発者は必要なプロジェクトのみセットアップ可能：

```bash
# バックエンドのみ開発
cd backend && uv sync

# Flutterのみ開発
cd flutter && flutter pub get

# 全体を起動（Docker Compose）
make up
```

## モノレポが適さなくなるケース

以下の状況が発生した場合、リポジトリ分割を検討：

1. **チームの分離**: 異なるチームが独立してリリースする必要がある
2. **セキュリティ要件**: 機密コードの分離が必要
3. **リポジトリサイズ**: cloneに数分以上かかるようになった
4. **ライセンス**: 異なるライセンスのコードが混在

## 参考資料

- [Monorepo vs Polyrepo](https://monorepo.tools/)
- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Git Subtree](https://www.atlassian.com/git/tutorials/git-subtree)
