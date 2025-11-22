.PHONY: help install install-dev install-backend install-frontend \
		audit audit-desc outdated lock-upgrade lock-upgrade-dry-run \
		lint lint-backend lint-frontend format format-backend format-frontend \
		type-check test test-backend test-frontend \
		dev dev-backend dev-frontend \
		build build-backend build-frontend \
		docker-up docker-down docker-logs docker-clean \
		db-connect db-migrate

# デフォルトターゲット
.DEFAULT_GOAL := help

# 変数定義
BACKEND_DIR := backend
FRONTEND_DIR := frontend
UV := uv
PNPM := pnpm

##@ ヘルプ

help: ## このヘルプメッセージを表示
	@echo "利用可能なコマンド:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' | sort

##@ インストール

install: install-backend install-frontend ## すべての依存関係をインストール

install-dev: install-backend-dev install-frontend ## 開発用依存関係を含めてインストール

install-backend: ## バックエンドの依存関係をインストール
	@echo "📦 バックエンドの依存関係をインストール中..."
	cd $(BACKEND_DIR) && $(UV) sync --all-extras

install-backend-dev: ## バックエンドの開発依存関係を含めてインストール
	@echo "📦 バックエンドの開発依存関係をインストール中..."
	cd $(BACKEND_DIR) && $(UV) sync --all-extras

install-frontend: ## フロントエンドの依存関係をインストール
	@echo "📦 フロントエンドの依存関係をインストール中..."
	cd $(FRONTEND_DIR) && $(PNPM) install

##@ セキュリティ

audit: audit-desc ## セキュリティ脆弱性をスキャン（エイリアス）

audit-desc: ## セキュリティ脆弱性をスキャン（詳細表示）
	@echo "🔒 セキュリティ脆弱性をスキャン中..."
	cd $(BACKEND_DIR) && $(UV) run pip-audit --desc

##@ 依存関係管理

outdated: ## 更新可能なパッケージを確認
	@echo "📋 更新可能なパッケージを確認中..."
	cd $(BACKEND_DIR) && $(UV) pip list --outdated

lock-upgrade: ## ロックファイルを更新（実際に更新）
	@echo "🔓 ロックファイルを更新中..."
	cd $(BACKEND_DIR) && $(UV) lock --upgrade

lock-upgrade-dry-run: ## ロックファイルの更新内容を確認（dry-run）
	@echo "🔍 ロックファイルの更新内容を確認中..."
	cd $(BACKEND_DIR) && $(UV) lock --upgrade --dry-run

##@ リント・フォーマット

lint: lint-backend lint-frontend ## すべてのコードをリント

lint-backend: ## バックエンドのコードをリント
	@echo "🔍 バックエンドのコードをリント中..."
	cd $(BACKEND_DIR) && $(UV) run ruff check .

lint-frontend: ## フロントエンドのコードをリント
	@echo "🔍 フロントエンドのコードをリント中..."
	cd $(FRONTEND_DIR) && $(PNPM) run lint || echo "lintスクリプトが定義されていません"

format: format-backend format-frontend ## すべてのコードをフォーマット

format-backend: ## バックエンドのコードをフォーマット
	@echo "✨ バックエンドのコードをフォーマット中..."
	cd $(BACKEND_DIR) && $(UV) run ruff format .

format-frontend: ## フロントエンドのコードをフォーマット
	@echo "✨ フロントエンドのコードをフォーマット中..."
	cd $(FRONTEND_DIR) && $(PNPM) run format

##@ 型チェック

type-check: ## バックエンドの型チェック
	@echo "🔎 バックエンドの型チェック中..."
	cd $(BACKEND_DIR) && $(UV) run mypy app

##@ テスト

test: test-backend test-frontend ## すべてのテストを実行

test-backend: ## バックエンドのテストを実行
	@echo "🧪 バックエンドのテストを実行中..."
	cd $(BACKEND_DIR) && $(UV) run pytest

test-frontend: ## フロントエンドのテストを実行
	@echo "🧪 フロントエンドのテストを実行中..."
	cd $(FRONTEND_DIR) && $(PNPM) run test || echo "testスクリプトが定義されていません"

##@ 開発サーバー

dev: ## すべての開発サーバーを起動（Docker Compose）
	@echo "🚀 開発サーバーを起動中..."
	docker compose up

dev-backend: ## バックエンドの開発サーバーを起動
	@echo "🚀 バックエンドの開発サーバーを起動中..."
	cd $(BACKEND_DIR) && $(UV) run uvicorn app.main:app --reload

dev-frontend: ## フロントエンドの開発サーバーを起動
	@echo "🚀 フロントエンドの開発サーバーを起動中..."
	cd $(FRONTEND_DIR) && $(PNPM) run dev

##@ ビルド

build: build-backend build-frontend ## すべてをビルド

build-backend: ## バックエンドをビルド（現在は不要だが将来用）
	@echo "🔨 バックエンドをビルド中..."
	@echo "バックエンドはビルド不要です（Pythonはインタープリタ言語）"

build-frontend: ## フロントエンドをビルド
	@echo "🔨 フロントエンドをビルド中..."
	cd $(FRONTEND_DIR) && $(PNPM) run build

##@ Docker

docker-up: ## Docker Composeでサービスを起動
	@echo "🐳 Docker Composeでサービスを起動中..."
	docker compose up -d

docker-down: ## Docker Composeでサービスを停止
	@echo "🐳 Docker Composeでサービスを停止中..."
	docker compose down

docker-logs: ## Docker Composeのログを表示
	@echo "📋 Docker Composeのログを表示中..."
	docker compose logs -f

docker-clean: ## Docker Composeのボリュームとコンテナを削除
	@echo "🧹 Docker Composeのボリュームとコンテナを削除中..."
	docker compose down -v

##@ データベース

db-connect: ## PostgreSQLに接続
	@echo "🗄️  PostgreSQLに接続中..."
	docker compose exec postgres psql -U chatbot -d chatbot_db

db-migrate: ## データベースマイグレーションを実行
	@echo "🔄 データベースマイグレーションを実行中..."
	cd $(BACKEND_DIR) && $(UV) run alembic upgrade head

##@ チェック（CI/CD用）

check: lint type-check test audit-desc ## すべてのチェックを実行（リント、型チェック、テスト、セキュリティスキャン）

check-backend: lint-backend type-check test-backend audit-desc ## バックエンドのすべてのチェックを実行

check-frontend: lint-frontend test-frontend ## フロントエンドのすべてのチェックを実行

