# ADR-0001: ADR（Architecture Decision Record）の作成を採用

- 日付: 2026-08-05
- ステータス: 採用(Accepted)

## 背景・課題
過去の設計判断を記録に残す必要がある。

## 選択肢
1. Architecture Decision Record に記録
2. Pull requests に記録

## 決定
両方を採用する。

## 理由
- PRでの記載はレビュー時に役立つ
- 過去のPRは流れてしまい、閲覧機会が限られるため、ADRとしてリポジトリに残す

## 結果・影響
- `./template.md` にテンプレを配置
- 設計判断を伴った際にテンプレをコピーしてADRを連番で作成する
