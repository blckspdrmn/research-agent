include .env
export

.PHONY: help build up down api-logs ps migrate revision seed lint format test ci shell-api psql

help: ## コマンド一覧を表示
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## 全コンテナをビルド
	docker compose up --build

up: ## 全コンテナを起動
	docker compose up -d

down: ## 停止(ボリュームは残す)
	docker compose down

api-logs: ## apiのログを追う
	docker compose logs -f api

ps: ## コンテナの状態
	docker compose ps

migrate: ## マイグレーションを適用
	docker compose exec api alembic upgrade head

revision: ## マイグレーションを自動生成(例: make revision m="add status")
	docker compose exec api alembic revision --autogenerate -m "$(m)"

seed: ## 開発用のダミーユーザーを投入
	docker compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) \
	  -c "INSERT INTO users (email) VALUES ('dev@example.com') ON CONFLICT DO NOTHING;"

lint: ## lint(CIと同じコマンド)
	cd api && uv run ruff check .
	cd api && uv run ruff format --check .

format: ## 自動整形
	cd api && uv run ruff check --fix . && uv run ruff format .

test:  ## テスト
	cd api && uv run pytest -q

ci: lint test ## CIと同じ検査をまとめて実行

shell-api: ## apiコンテナに入る
	docker compose exec api bash

psql: ## psqlに入る
	docker compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
