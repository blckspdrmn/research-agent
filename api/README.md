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
| `TEST_DATABASE_URL` | テスト実行時の接続先。開発用とは**別のデータベース**を指定する ([テスト](#テスト)) |
| `DUMMY_USER_ID` | 認証実装までの暫定値。[初期データ](#初期データ)で採番された UUID を設定する |

`<ユーザー名>` `<パスワード>` `<データベース名>` は任意に決めてよい。ただし**下記のコンテナ起動時に指定する値と一致させること**。

- `.env` は Git 管理外 (`.gitignore`)。認証情報を含むためコミットしないこと
- 設定の読み込みは `config.py` の `Settings` (pydantic-settings) が担当する
- `env_file` を相対パスで指定しているため、**コマンドは `api/` ディレクトリ上で実行する**こと。別の階層から実行すると `.env` が読まれず起動時に検証エラーになる
- `DUMMY_USER_ID` は UUID として検証される。形式が不正な場合は起動時にエラーで停止する
- `TEST_DATABASE_URL` は未設定でもアプリは起動する (テスト実行時のみ必要なため)

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

## マイグレーション (Alembic)

コンテナを起動しただけではテーブルは存在しない。**初回セットアップ時と、モデル変更を取り込んだときは必ず実行する**。

```bash
uv run alembic upgrade head    # 最新まで適用
```

| コマンド | 内容 |
|---|---|
| `uv run alembic current` | 適用済みのリビジョンを表示 |
| `uv run alembic history` | マイグレーションの履歴を表示 |
| `uv run alembic upgrade head --sql` | DB に適用せず、実行される SQL だけを出力 |
| `uv run alembic revision --autogenerate -m "<説明>"` | モデルとの差分からマイグレーションを生成 |
| `uv run alembic downgrade -1` | 1つ前に戻す |

- **コマンドは `api/` ディレクトリ上で実行する**こと。`alembic.ini` の `prepend_sys_path = .` が実行時のカレントディレクトリを import パスに加えるため、別の階層からだと `ModuleNotFoundError: No module named 'config'` になる
- 接続先は `alembic.ini` の `sqlalchemy.url` ではなく、`migrations/env.py` が `.env` から読み込む
- `--autogenerate` で生成したファイルは、**適用する前に必ず内容を確認する**こと。特にテーブル名・列名の変更(リネーム)は検出できず、「削除 + 追加」と解釈されてデータが失われる

## 初期データ

認証が未実装のため、テーマの所有者となるユーザーを1件手動で投入する。**ID は DB 側が採番する**ので、`RETURNING` で受け取って `.env` に設定する。

```bash
docker exec -it research-agent-db psql -U <ユーザー名> -d <データベース名> \
  -c "INSERT INTO users (email) VALUES ('dev@example.com') RETURNING id;"
```

表示された UUID を `.env` の `DUMMY_USER_ID` に設定する。

> **注意**: この手順は認証を実装するまでの暫定措置。実装時に `DUMMY_USER_ID` と本セクションは削除する。

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

## テスト

テストは開発用とは別のデータベースに対して実行する。初回のみ作成が必要。

```bash
docker exec -it research-agent-db psql -U <ユーザー名> -d postgres \
  -c "CREATE DATABASE <データベース名>_test;"
```

作成したデータベースを `.env` の `TEST_DATABASE_URL` に設定してから実行する。

```bash
uv run pytest         # 全テスト
uv run pytest -q      # 結果のみ簡潔に表示
uv run pytest -k <キーワード>   # 名前でテストを絞り込む
```

> **⚠️ `TEST_DATABASE_URL` を開発用データベースに向けないこと**
>
> テストは実行のたびに**全テーブルを削除して作り直す** (`conftest.py`)。誤って開発用を指していると開発データが失われる。事故防止として、データベース名が `_test` で終わらない場合はテストが起動しないようにしてある。

- テスト用のテーブルはマイグレーションではなくモデル定義から直接作成している。そのため**マイグレーションの正しさはテストでは検証されない**
- HTTP リクエストは `httpx.ASGITransport` でアプリを直接呼び出しており、サーバーの起動は不要

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
