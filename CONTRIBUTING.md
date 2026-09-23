# 開発者向けガイド

ローカル環境の準備から変更をPull Requestとしてマージするまでの手順です。アプリの概要と構成は[README.md](README.md)を参照してください。

## 前提ツール

- Docker Desktop（Docker Composeを含む）
- Node.js 24
- [uv](https://docs.astral.sh/uv/)（Pythonのエディタ補完環境を作る場合）
- `make`
- Azure CLI（本番環境を操作する必要がある場合のみ）

アプリ起動、lint、APIテストはDocker Compose上で実行します。エディタの補完や型チェックに使うPython環境は、必要に応じて次のコマンドで作成できます。

```bash
cd api
uv sync
```

## 初回セットアップ

### 1. 環境変数ファイルを用意する

```bash
cp .env.example .env
cp api/.env.example api/.env
cp frontend/.env.local.example frontend/.env.local
```

`api/.env`と`frontend/.env.local`のプレースホルダーを実際の値に置き換えます。Microsoft Entra External IDでは、次の2つのアプリ登録が必要です。

- API用: アプリケーション（クライアント）IDと公開するスコープを確認する
- Web用: アプリケーション（クライアント）ID、クライアントシークレットを作成し、`http://localhost:3001/api/auth/callback/microsoft-entra-id`をリダイレクトURIに登録する
- 外部テナントのOpenID Connectディスカバリ文書から`issuer`、`jwks_uri`、`end_session_endpoint`を確認する

値そのものをドキュメントやGit管理対象へ記載しないでください。

### 2. 起動してDBを準備する

```bash
make up
make migrate
make test-db  # 初回のみ
```

| URL | 用途 |
| --- | --- |
| <http://localhost:3001> | フロントエンド |
| <http://localhost:8000/health> | APIヘルスチェック |
| <http://localhost:8000/docs> | Swagger UI |
| <http://localhost:8000/openapi.json> | OpenAPI定義 |

APIは`--reload`で起動するため、`api/`の変更は自動反映されます。workerは自動反映されないため、コード変更後に再起動してください。

## 環境変数

### ルート `.env`

| 変数名 | 用途 | 取得元 |
| --- | --- | --- |
| `POSTGRES_USER` | ローカルDBのユーザー名 | `.env.example`の開発用初期値 |
| `POSTGRES_PASSWORD` | ローカルDBのパスワード | `.env.example`の開発用初期値 |
| `POSTGRES_DB` | ローカルDB名 | `.env.example`の開発用初期値 |

### `api/.env`

| 変数名 | 用途 | 取得元 |
| --- | --- | --- |
| `AZURE_OPENAI_BASE_URL` | Microsoft FoundryのOpenAI互換エンドポイント | Foundryポータル |
| `AZURE_OPENAI_API_KEY` | LLMの認証キー | Foundryポータル |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | チャットモデルのデプロイ名 | Foundryポータル |
| `TAVILY_API_KEY` | Web検索の認証キー | Tavilyの管理画面 |
| `ENTRA_ISSUER` | トークン発行者の検証値 | OpenID Connectディスカバリ文書の`issuer` |
| `ENTRA_JWKS_URL` | 署名検証用公開鍵の取得先 | 同文書の`jwks_uri` |
| `ENTRA_API_CLIENT_ID` | トークンの宛先を検証するAPIのクライアントID | API用アプリ登録 |
| `ENTRA_REQUIRED_SCOPE` | APIが要求するスコープ | API用アプリ登録で公開したスコープ |

`DATABASE_URL`、`TEST_DATABASE_URL`、`AZURE_STORAGE_CONNECTION_STRING`はローカルでは`compose.yaml`が注入します。必須値が不足すると設定チェックによりコンテナ起動時に停止します。

### `frontend/.env.local`

| 変数名 | 用途 | 取得元 |
| --- | --- | --- |
| `API_URL_INTERNAL` | Next.jsサーバーからAPIへの接続先 | サンプル値。Compose起動時は`compose.yaml`が上書き |
| `AUTH_URL` | Auth.jsが使うフロントエンドのURL | ローカルではブラウザからアクセスするURL |
| `AUTH_SECRET` | Auth.jsのセッション暗号化用シークレット | ローカルで生成した十分に長いランダム値 |
| `AUTH_MICROSOFT_ENTRA_ID_ID` | WebのクライアントID | Web用アプリ登録 |
| `AUTH_MICROSOFT_ENTRA_ID_SECRET` | Webのクライアントシークレット | Web用アプリ登録で作成したシークレット値 |
| `AUTH_MICROSOFT_ENTRA_ID_ISSUER` | 認証を行う発行者 | OpenID Connectディスカバリ文書の`issuer` |
| `AUTH_ENTRA_API_SCOPE` | APIアクセストークンで要求するスコープ | API用アプリ登録 |
| `AUTH_ENTRA_LOGOUT_URL` | Entraのログアウト先 | OpenID Connectディスカバリ文書の`end_session_endpoint` |

`AUTH_URL`はローカルでも必須です。ブラウザが使うポートとコンテナ内でNext.jsが待ち受けるポートが異なるため、省略できません。

## よく使うコマンド

| コマンド | 内容 |
| --- | --- |
| `make help` | 利用できるコマンドを一覧表示 |
| `make build` | 全コンテナをビルドして起動 |
| `make up` / `make down` | 全コンテナを起動 / 停止 |
| `make ps` | コンテナの状態を表示 |
| `make api-logs` | APIログを追跡 |
| `make migrate` | DBマイグレーションを適用 |
| `make revision m="説明"` | マイグレーションを自動生成 |
| `make test-db` | テストDBを作成（初回のみ） |
| `make test` | APIテストを実行 |
| `make lint` / `make format` | APIの検査 / 自動整形 |
| `make ci` | CI相当のAPI・frontend検査をまとめて実行 |
| `make npm-install` | frontendコンテナ内で依存関係を更新 |
| `make shell-api` / `make psql` | APIシェル / psqlを開く |

## 開発の流れ

1. 最新の`main`から`feat/...`、`fix/...`、`docs/...`、`chore/...`のいずれかでブランチを作成します。
2. 変更とテストを追加し、`make ci`で確認します。
3. コミットメッセージは`{conventional}: {日本語で変更内容}`形式にします（例: `feat: リサーチ結果の表示を追加`）。
4. [Pull Requestテンプレート](.github/pull_request_template.md)に沿って背景、設計判断、動作確認を記載します。
5. CI通過とレビュー後にsquash mergeします。

squash mergeしたブランチは使い回さず、次の変更は更新した`main`から新しいブランチを作成してください。元ブランチを再利用すると、squash前の履歴が残って競合しやすくなります。

## DBマイグレーション

```bash
make revision m="変更内容"
# api/migrations/versions/ の生成物を確認する
make format
make migrate
```

Alembicの自動生成結果は必ず確認してください。特にテーブル名・列名の変更は「削除＋追加」と誤検出され、データを失う可能性があります。自動生成ファイルはそのままではruffを通らない場合があるため、確認後に`make format`を実行します。

履歴確認には`docker compose exec api alembic current`と`docker compose exec api alembic history`を使えます。テストDBはテストのたびに全テーブルを作り直すため、`TEST_DATABASE_URL`を開発DBへ向けないでください。また、テストはモデルからテーブルを作るため、マイグレーション自体の正しさは別途確認が必要です。

## テストとlint

```bash
make ci      # CI相当の一括検査
make test    # APIテスト
make lint    # APIのlint・formatチェック
make format  # APIの自動整形

cd frontend
npm run format:check
npm run lint
npm run build
```

## CI/CD

- GitHubのPull Request: APIはDocker Compose上でruffとpytest、frontendはPrettier、ESLint、Next.js buildを実行します。CIが成功しない変更はマージできません。
- `main`へのマージ: `az acr build`でAPIとfrontendのイメージをACRへ保存します。
- Migrate: 新しいAPIイメージで`api-migrate`を起動し、`alembic upgrade head`の完了を待ちます。失敗時はデプロイしません。
- 承認: Azure DevOps Environmentの`production`で承認します。
- Deploy: API、frontend、research-workerを新しいイメージへ更新します。

Azureへの認証にはWorkload Identity federationを設定したService Connectionを使い、長期キーは保存しません。APIイメージはAPI、worker、migrateで共用し、起動コマンドだけを変えています。

本番向けの環境変数を追加した場合は、対応コードをデプロイする前にContainer Appsの`api`、`research-worker`、`api-migrate`、`frontend`へ必要な値を設定してください。不足すると起動時の設定チェックで停止します。

## 設計判断の記録

既存の判断は[docs/adr/](docs/adr/)を参照してください。今後の重要な設計判断もADRとして追加します。

## 秘密情報の扱い

- `.env`、`api/.env`、`frontend/.env.local`などの実値をコミットしないでください。
- APIキー、クライアントシークレット、接続文字列、クラウドの識別子や公開前のURLをIssue、Pull Request、ログへ貼らないでください。
- コミット前に`git diff --staged`を確認し、秘密情報や不要な生成物が含まれていないことを確認してください。

## その他注意点

- ホストでの`npm ci` / `npm install`はエディタ補完・lint・build用として正しい手順です。一方、frontendコンテナの`node_modules`は別の名前付きボリュームにあるため、依存を追加・更新したら`make npm-install`でコンテナ側にも反映します。
- frontendの再起動には`docker compose up -d --force-recreate frontend`を使います。`docker compose restart frontend`では名前付きボリュームが外れ、ホストのmacOS用ネイティブバイナリ（lightningcssなど）がコンテナから見えて起動に失敗する場合があります。
- Turbopackのキャッシュが壊れた場合は`docker volume rm research-agent_frontend_next`で対象ボリュームだけを削除します。`docker compose down -v`はDBのボリュームも削除するため使わないでください。
- `AUTH_URL`はローカルでも設定します。ブラウザのポートとコンテナ内のポートが異なります。
- workerはコード変更を自動で読み込みません。`docker compose up -d --force-recreate worker`で再起動します。
