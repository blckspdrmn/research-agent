# api

Research Agent のバックエンド (FastAPI)。

## 前提

- [uv](https://docs.astral.sh/uv/) がインストールされていること
- Python 3.12 (`.python-version` で固定。uv が自動で用意する)
- Docker (開発用 PostgreSQL の起動に使用)

## セットアップ

```bash
uv sync   # pyproject.toml / uv.lock から api/.venv を作成し依存をインストール
```

## 環境変数

`.env.example` をコピーして `.env` を作成する。

```bash
cp .env.example .env
```

| 変数 | 内容 |
|---|---|
| `DATABASE_URL` | 接続先 PostgreSQL。`postgresql+psycopg://<ユーザー名>:<パスワード>@localhost:5432/<データベース名>` |

`<ユーザー名>` `<パスワード>` `<データベース名>` は任意に決めてよい。ただし**下記のコンテナ起動時に指定する値と一致させること**。

- `.env` は Git 管理外 (`.gitignore`)。認証情報を含むためコミットしないこと
- 設定の読み込みは `config.py` の `Settings` (pydantic-settings) が担当する
- `env_file` を相対パスで指定しているため、**コマンドは `api/` ディレクトリ上で実行する**こと。別の階層から実行すると `.env` が読まれず起動時に検証エラーになる

## データベース (PostgreSQL)

開発用の PostgreSQL はコンテナで起動する。`<...>` の部分は `.env` の `DATABASE_URL` に書いた値と揃えること。

```bash
docker run -d \
  --name research-agent-db \
  -e POSTGRES_USER=<ユーザー名> \
  -e POSTGRES_PASSWORD=<パスワード> \
  -e POSTGRES_DB=<データベース名> \
  -p 5432:5432 \
  -v research-agent-pgdata:/var/lib/postgresql \
  postgres:18
```

| オプション | 内容 |
|---|---|
| `-e POSTGRES_USER` / `_PASSWORD` / `_DB` | 初回起動時に作成される初期ユーザー / パスワード / データベース名 |
| `-p 5432:5432` | ホストの 5432 番をコンテナへ転送 |
| `-v research-agent-pgdata:/var/lib/postgresql` | データを名前付きボリュームへ永続化 |

> **注意**: `POSTGRES_*` が効くのは**ボリュームが空の初回起動時のみ**。あとから値を変えてもコンテナを作り直すだけでは反映されない（既存データが優先される）。変更したい場合はボリュームごと削除して作り直す。

日常的な操作:

```bash
docker ps                          # 起動確認
docker logs research-agent-db      # 起動失敗時はまずこれを見る
docker stop research-agent-db      # 停止
docker start research-agent-db     # 再開
docker exec -it research-agent-db psql -U <ユーザー名> -d <データベース名>   # psql で接続
```

データごと作り直したい場合はボリュームも削除する (**データは失われる**)。

```bash
docker rm -f research-agent-db
docker volume rm research-agent-pgdata
```

※ 現状は `docker run` を手で叩く運用。将来的に Docker Compose へ移行する。

## 起動

```bash
uv run uvicorn main:app --reload --port 8000
```

- `main:app` = `main.py` の `app` 変数
- `--reload` = ファイル変更を検知して自動再起動 (開発用)

## 動作確認

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}
```

| URL | 内容 |
|---|---|
| http://localhost:8000/health | ヘルスチェック |
| http://localhost:8000/docs | Swagger UI (ブラウザから API を試せる) |
| http://localhost:8000/openapi.json | OpenAPI 定義 (自動生成) |

## Lint / Format

Ruff を使用。ルールは `pyproject.toml` の `[tool.ruff]` に定義。

```bash
uv run ruff check .         # lint
uv run ruff check --fix .   # 自動修正できるものを修正
uv run ruff format .        # フォーマット
```

リポジトリルートで `pre-commit install` 済みなら、コミット時に自動で実行される。

## VS Code

仮想環境はリポジトリルート直下ではなく `api/.venv` にあるため、初回は
`Python: Select Interpreter` で `./api/.venv/bin/python` を選択する。
