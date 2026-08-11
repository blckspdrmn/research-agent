# research-agent

テーマを登録すると、AIエージェントが定期的にWebリサーチしてレポートを作るアプリ。

学習目的のため、Claude Codeに知らない概念等を質問しつつ実装を試みる。

## 開発環境のセットアップ

```bash
cp .env.example .env
cp api/.env.example api/.env
make up
make migrate
make seed
```

`make seed`が表示する`id`を`api/.env`の`DUMMY_USER_ID`に設定し(認証未実装のための暫定措置。詳細は[api/README](api/README.md)参照)、反映させる。

```bash
make restart-api
```

http://localhost:8000/docs でAPIドキュメントを確認できる。

その他のコマンドは `make help` を参照。
