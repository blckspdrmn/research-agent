# ADR-0004: フロントエンドからのAPI呼び出しにServer Actionsを使う

- 日付: 2026-08-15
- ステータス: 採用(Accepted)

## 背景・課題

フロントエンド（Next.js）からバックエンド（FastAPI）へのデータ送信（作成・更新・削除）をどの経路で行うかを決める必要がある。

本番ではFastAPIは外部に公開しない前提である。
（Docker内部ネットワーク上にあり、ブラウザからは直接到達できない。ブラウザに公開する場合、CORS設定やサーバー用URL・ブラウザ用URLの二重管理が必要になる。）

## 選択肢

1. **ブラウザからFastAPIを直接呼ぶ** — FastAPIをブラウザに公開し、CORS設定を追加する
2. **Next.js Route Handlers（API Routes）を中継する** — `/api/*` エンドポイントを自前で定義し、そこからFastAPIに転送する
3. **Next.js Server Actionsを中継する** — `"use server"` 関数からFastAPIを呼ぶ

## 決定

選択肢3: Server Actionsを採用する。

## 理由

- FastAPIをDocker内部に隠したまま運用できる。ブラウザから見えるのはNext.jsのみとなり、攻撃面が小さい
- `useActionState` との連携により、送信中（pending）・エラー・成功の状態管理をフレームワーク側に任せられる
- Route Handlersでも中継は可能だが、フォーム送信→結果表示の流れにおいてはServer Actionsの方がボイラープレートが少ない

## 結果・影響

- データ送信は `actions.ts`（`"use server"`）に集約される
- データ取得（GET）はServer Componentから `api.ts` の関数を直接呼ぶ構成とし、Server Actionsは使わない
