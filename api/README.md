# api

Research Agent のバックエンド (FastAPI)。

アプリの起動・lint・テストは**すべて Docker Compose 経由(コンテナ内)で実行する**。ホスト (Mac) 上で直接 `uv run uvicorn` 等を実行する運用はしていない (CI もコンテナ内で実行する予定であるため、手元とCIの実行環境を揃えてある)。

## 前提

- Docker (`docker compose up` で PostgreSQL・API コンテナを起動する。lint/test もこのコンテナ内で実行する)
- [uv](https://docs.astral.sh/uv/) がインストールされていること (アプリの実行には不要。VS Code 等のエディタでコード補完・型チェックを効かせるためだけに使う)

## セットアップ

エディタ補完用にホストにも `.venv` を作成しておく (任意。無くてもコンテナは動く)。

```bash
uv sync   # pyproject.toml / uv.lock から api/.venv を作成し依存をインストール
```

## 環境変数

`.env.example` をコピーして `.env` を作成する(ルートREADMEの`cp api/.env.example api/.env`と同じ操作。実施済みならスキップ)。

```bash
cp .env.example .env
```

| 変数 | 内容 |
|---|---|
| `DUMMY_USER_ID` | 認証実装までの暫定値。[初期データ](#初期データ)で採番された UUID を設定する |

- `.env` は Git 管理外 (`.gitignore`)。認証情報を含むためコミットしないこと
- 設定の読み込みは `config.py` の `Settings` (pydantic-settings) が担当する
- `DUMMY_USER_ID` は UUID として検証される。形式が不正な場合はコンテナ起動時にエラーで停止する

## データベース (PostgreSQL)

開発用の PostgreSQL は、リポジトリルートの Docker Compose で起動する (詳細は[ルートの README](../README.md))。

```bash
# リポジトリルートで
make up
```

日常的な操作はリポジトリルートの `make help` を参照。psql で直接繋ぐ場合:

```bash
# リポジトリルートで
docker compose exec db psql -U <ユーザー名> -d <データベース名>
```

## マイグレーション (Alembic)

コンテナを起動しただけではテーブルは存在しない。**初回セットアップ時と、モデル変更を取り込んだときは必ず実行する**。

```bash
# リポジトリルートで
make migrate
```

`docker compose exec api alembic upgrade head` と同じ内容。

| コマンド | 内容 |
|---|---|
| `docker compose exec api alembic current` | 適用済みのリビジョンを表示 |
| `docker compose exec api alembic history` | マイグレーションの履歴を表示 |
| `docker compose exec api alembic upgrade head --sql` | DB に適用せず、実行される SQL だけを出力 |
| `make revision m="<説明>"` | モデルとの差分からマイグレーションを生成 |
| `docker compose exec api alembic downgrade -1` | 1つ前に戻す |

- `--autogenerate` (`make revision`) で生成したファイルは、**適用する前に必ず内容を確認する**こと。特にテーブル名・列名の変更(リネーム)は検出できず、「削除 + 追加」と解釈されてデータが失われる

## 初期データ

認証が未実装のため、テーマの所有者となるユーザーを1件手動で投入する。**ID は DB 側が採番する**ので、`RETURNING` で受け取って `.env` に設定する。

```bash
# リポジトリルートで
make seed
```

表示された `id` を `api/.env` の `DUMMY_USER_ID` に設定し、反映させる。

```bash
# リポジトリルートで
make restart-api
```

> **注意**: この手順は認証を実装するまでの暫定措置。実装時に `DUMMY_USER_ID` と本セクションは削除する。
>
> **⚠️ Docker Compose環境でDBを作り直したとき(`docker compose down -v`など)は、この手順をやり直すこと。** 新しいDBでは`DUMMY_USER_ID`が指すユーザーが存在しなくなり、`POST /themes`等が`ForeignKeyViolation`で500エラーになる。

## 起動

リポジトリルートで `make up`(詳細は[データベース](#データベース-postgresql)節、および[ルートの README](../README.md))。`api` コンテナは `--reload` 付きで起動しており、ホスト側 (`./api`) のファイル編集が即座に反映される。

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
# リポジトリルートで
make test-db
```

実行:

```bash
# リポジトリルートで
make test
```

`docker compose exec api pytest -q` と同じ内容。キーワード指定など細かいオプションを使いたい場合:

```bash
docker compose exec api pytest -k <キーワード>   # 名前でテストを絞り込む
```

> **⚠️ `TEST_DATABASE_URL` を開発用データベースに向けないこと**
>
> テストは実行のたびに**全テーブルを削除して作り直す** (`conftest.py`)。誤って開発用を指していると開発データが失われる。事故防止として、データベース名が `_test` で終わらない場合はテストが起動しないようにしてある(`compose.yaml` の `TEST_DATABASE_URL` は最初から `_test` 付きのDB名になっている)。

- テスト用のテーブルはマイグレーションではなくモデル定義から直接作成している。そのため**マイグレーションの正しさはテストでは検証されない**
- HTTP リクエストは `httpx.ASGITransport` でアプリを直接呼び出しており、サーバーの起動は不要

## Lint / Format

Ruff を使用。ルールは `pyproject.toml` の `[tool.ruff]` に定義。

```bash
# リポジトリルートで
make lint     # lint(CIと同じ検査)
make format   # 自動修正
make ci       # lint + test
```

`docker compose exec api ruff check .` 等と同じ内容(`uv`本体は実行用イメージに含まれていないため、`uv run`を挟まず直接呼び出している)。`pre-commit install` 済みなら、コミット時にも自動で実行される。

## VS Code

補完・型チェックのために、ホスト側にも `.venv` を用意しておく([セットアップ](#セットアップ)参照)。仮想環境はリポジトリルート直下ではなく `api/.venv` にあるため、初回は
`Python: Select Interpreter` で `./api/.venv/bin/python` を選択する。

## Docker イメージについて

`api/Dockerfile` はマルチステージ構成で、`production`(本番用、lint/testツールを含まない軽量版)と `dev`(ローカル開発用、ruff/pytest等を含む)の2つのビルドターゲットを持つ。`compose.yaml` は `target: dev` を指定してビルドしており、`make lint`/`make test`はこの`dev`イメージの中で実行される。本番デプロイでは `production` ターゲット(Dockerfileの既定の最終ステージ)を使う予定。
