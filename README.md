# research-agent

テーマを登録すると、AIエージェントが定期的にWebリサーチしてレポートを作るアプリ。

学習目的のため、Claude Codeに知らない概念等を質問しつつ実装を試みる。

## 構成

| ディレクトリ | 中身                             |
| ------------ | -------------------------------- |
| `frontend/`  | Next.js (App Router) + shadcn/ui |
| `api/`       | FastAPI + SQLAlchemy + LangChain |
| `docs/`      | ADR（設計判断の記録）            |

## 必要なもの

Docker Desktop / Node.js 24 / Python 3.12+ / uv / make（Macは標準）

## セットアップ

```bash
cp .env.example .env           # DBの認証情報（デフォルト値のままでよい）
cp api/.env.example api/.env
cp frontend/.env.local.example frontend/.env.local # Docker Compose経由なら不要
make up                        # 全コンテナ起動
make migrate                   # DBスキーマ適用
make seed                      # ダミーユーザー投入
```

`make seed`が表示する`id`を`api/.env`の`DUMMY_USER_ID`に設定し(認証未実装のための暫定措置。詳細は[api/README](api/README.md)参照)、反映させる。

```bash
make restart-api
```

- フロント: http://localhost:3001
- API（Swagger UI）: http://localhost:8000/docs

## 環境変数

| 変数                                                  | 用途                                   | 取得元                                         |
| ----------------------------------------------------- | -------------------------------------- | ---------------------------------------------- |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | ローカルDBの認証情報                   | `.env.example`のデフォルト値のままでよい       |
| `DUMMY_USER_ID`（`api/.env`）                         | 認証未実装のため暫定的に使うユーザーID | `make seed`が表示するid                        |
| `AZURE_OPENAI_BASE_URL`（`api/.env`）                 | Azure OpenAIのエンドポイント           | Azure AI Foundryポータル                       |
| `AZURE_OPENAI_API_KEY`（`api/.env`）                  | Azure OpenAIのAPIキー                  | Azure AI Foundryポータル                       |
| `AZURE_OPENAI_CHAT_DEPLOYMENT`（`api/.env`）          | チャットモデルのデプロイ名             | Azure AI Foundryポータル                       |
| `TAVILY_API_KEY`（`api/.env`）                        | Web検索用のTavily APIキー              | [Tavily](https://tavily.com/)                  |
| `API_URL_INTERNAL`（`frontend/.env.local`）           | フロントエンドからAPIへの接続先URL     | `.env.local.example`のデフォルト値のままでよい |

## よく使うコマンド

`make help` を実行（全コマンドの一覧が出る）

## CI

PRを出すとAzure DevOps上でlint / test / buildが自動実行される。CIが通らないとマージできない。

## ドキュメント

- 設計判断の履歴: `docs/adr/`
