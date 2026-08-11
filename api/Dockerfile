# マルチステージビルド

# ---- ステージ1（builderステージ）: 依存関係を解決し、仮想環境を作成(本番用、devツールなし) ----
# ベースとなるイメージを指定（Linux環境が含まれる）
FROM python:3.12-slim AS builder

# uvバイナリファイルを公式イメージからコピーして使う（必ずバージョンを固定する）
# builderステージの中の/usr/local/bin/は既定で$PATHに含まれるので、そこに置くことでuvコマンドが使える
COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /usr/local/bin/uv

# 以降のコマンドが実行される基準となるディレクトリ
WORKDIR /app

# 依存の再インストールが起こらないように先に依存インストール（レイヤーキャッシュを効かせる）
# /app/.venvが作成される。--no-devで本番に不要なruff/pytest等は入れない
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# ---- ステージ2（dev-builderステージ）: 開発用の依存を追加解決(ruff/pytest等を含む) ----
# builderの.venvに開発依存を追加インストールする(--no-devを外すだけ)
FROM builder AS dev-builder
RUN uv sync --frozen

# ---- ステージ3（baseステージ）: 実行用の共通土台 ----
# まっさらなベースイメージを用意
FROM python:3.12-slim AS base

# Dockerではデフォルトでrootユーザーとして振る舞う
# 侵入されたときの被害を抑えるため、appuserという一般ユーザーを作成する（まだ切り替えない）
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# 環境変数設定
# ①$PATHの先頭に仮想環境内のbinを追加（後で用いるuvicornコマンドが見つかるようになる）
# ②Pythonのコンパイル結果のキャッシュを無効化（コンテナは使い捨てなので恩恵がない）
# ③Pythonのログバッファリング（ある程度たまってから出力）を止めてリアルタイム出力化
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# .dockerignoreで指定したものを除いてapiディレクトリからすべてを/appにコピー
# ファイル所有者をrootではなくappuserユーザー、appuserグループにする（なお、ディレクトリの所有者は依然としてroot）
COPY --chown=appuser:appuser . .

# ---- ステージ4（devステージ）: 開発用イメージ(ruff/pytestを含み、compose.yamlから使う) ----
FROM base AS dev

# dev-builderから仮想環境をコピー(ruff/pytest等の開発ツールも含む)
# まだroot実行権限なのでディレクトリをコピーできる
COPY --from=dev-builder /app/.venv /app/.venv

# 実行者をappuserに切り替える
USER appuser

# このイメージはポート8000を使うという宣言
EXPOSE 8000

# ビルド時に実行するRUNに対して、CMDは起動時に実行
# --host 0.0.0.0: コンテナ自身からの通信以外も受け付けるように
# 開発用なのでreloadあり
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---- ステージ5（productionステージ）: 本番用の軽量イメージ ----
# Dockerfile内で最後に定義したステージが、--targetを指定しないdocker buildの既定になる。
FROM base AS production

# builderから仮想環境だけをコピー(uv本体やビルドキャッシュ、devツールは持ち込まない)
COPY --from=builder /app/.venv /app/.venv

USER appuser

EXPOSE 8000

# 本番用なのでreloadなし
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
