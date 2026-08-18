include .env
export

.PHONY: help build up down restart-api api-logs ps migrate revision seed test-db lint format test ci ci-api ci-frontend shell-api psql down-clean npm-install

help: ## コマンド一覧を表示
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## 全コンテナをビルド
	docker compose up --build

up: ## 全コンテナを起動
	docker compose up -d

down: ## 停止(ボリュームは残す)
	docker compose down

restart-api: ## apiコンテナを再起動(api/.env変更を反映させたいときに使う)
	docker compose restart api

api-logs: ## apiのログを追う
	docker compose logs -f -t api

ps: ## コンテナの状態
	docker compose ps

migrate: ## マイグレーションを適用
	docker compose exec api alembic upgrade head

revision: ## マイグレーションを自動生成(例: make revision m="add status")
	docker compose exec api alembic revision --autogenerate -m "$(m)"

seed: ## 開発用のダミーユーザーを投入(表示されたidをapi/.envのDUMMY_USER_IDに設定し、make restart-apiで反映すること)
	docker compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) \
	  -c "INSERT INTO users (email) VALUES ('dev@example.com') ON CONFLICT DO NOTHING RETURNING id;"

test-db: ## テスト用データベースを作成(初回のみ)
	docker compose exec db psql -U $(POSTGRES_USER) -d postgres \
	  -c "CREATE DATABASE $(POSTGRES_DB)_test;"

lint: ## lint
	docker compose exec api ruff check --no-cache .
	docker compose exec api ruff format --no-cache --check .

format: ## 自動整形
	docker compose exec api ruff check --fix .
	docker compose exec api ruff format .

test:  ## テスト (--junit-xml: Azure DevOps PublishTestResultsタスク用)
	docker compose exec api pytest -q --junit-xml=/tmp/results.xml

ci: ci-api ci-frontend ## CIと同じ検査をまとめて実行

ci-api: lint test ## APIのlint・テスト（CIでも利用）

ci-frontend: ## フロントエンドのlint・build（CIと同じ検査）
	cd frontend && npm run format:check && npm run lint && npm run build

shell-api: ## apiコンテナに入る
	docker compose exec api bash

psql: ## psqlに入る
	docker compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

npm-install: ## frontendコンテナ内でnpm install(パッケージ追加後に実行)
	docker compose exec frontend npm install

down-clean: ## 停止&ボリュームも削除してまっさらに(環境が自動破棄されないSelf Hosted AgentによるCI用)
	docker compose down -v --remove-orphans
