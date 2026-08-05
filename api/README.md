# api

Research Agent のバックエンド (FastAPI)。

## 前提

- [uv](https://docs.astral.sh/uv/) がインストールされていること
- Python 3.12 (`.python-version` で固定。uv が自動で用意する)

## セットアップ

```bash
uv sync   # pyproject.toml / uv.lock から api/.venv を作成し依存をインストール
```

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
