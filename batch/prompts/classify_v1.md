# ネタ分類プロンプト v1

## 入力情報

```
{
  "video_id": "YouTube動画ID",
  "title": "動画タイトル",
  "description": "動画説明文",
  "channel_name": "チャンネル名",
  "channel_kind": "comedian|agency|contest|tv|theater|other",
  "duration_sec": 秒数,
  "performer_names": ["芸人名1", "芸人名2"],
  "existing_tags": ["konbini", "mensetsu", ...],  // 既存タグリスト
  "contest_info": {  // 該当する場合のみ
    "slug": "m1|kotc|...",
    "year": 2024,
    "round": "final_1st|..."
  }
}
```

## 指示

以下のJSON形式で、この動画内のネタを分析してください。

### 分析対象
- 公式チャンネルでアップロードされた漫才・コント・ピン動画
- 不適切な動画（例：メイキング、フリートーク、広告）は `is_neta: false`

### 判定ルール

1. **is_neta**: これが実際のネタパフォーマンスか？
   - TRUE: 本編の漫才/コント/ピン
   - FALSE: メイキング、フリートーク、インタビュー、ショート集、広告など

2. **format**: 形式は何か？
   - `manzai`: 漫才（二人以上による掛け合い）
   - `conte`: コント（劇的シーン、設定ありの演技）
   - `pin`: ピン芸（一人芸、モノマネ、奇想天外など）
   - `other`: 分類不可

3. **confidence**: このネタ判定の確信度（0.0～1.0）
   - 1.0: 確実に本編ネタ
   - 0.7～0.9: おそらくネタだが曖昧な部分あり
   - 0.5～0.7: メイキングとネタが混在など
   - 0.0～0.5: ほぼメイキングやフリートークが占める

4. **performers**: 実際に登場する芸人名のリスト
   - 入力の `performer_names` に基づいて確認
   - 登場していない者は除外

5. **segments**: 複数のネタが含まれる場合は分割
   - 例: M-1決勝で複数組が登場
   - `start_sec`: 開始秒数
   - `end_sec`: 終了秒数
   - `neta_title`: 当該サイトでの一行説明（ある場合）、ない場合は `null`
   - 単一ネタの場合は1要素のリスト

6. **setting_tags**: 設定に関連するタグ
   - 必ず `existing_tags` から選択すること
   - 新規タグは `new_tag_proposals` に入れる
   - 例: "konbini", "part_timer", "mensetsu"

7. **new_tag_proposals**: 既存タグに該当しない新規タグ提案
   - 複数提案可能
   - 形式: `{"slug": "tag_slug", "name": "表示名", "category": "place|relation|job|theme|style"}`
   - 例: `{"slug": "convenience_store_worker", "name": "コンビニ店員（詳細）", "category": "job"}`

8. **contest**: 賞レース出演の場合のみ入力済みの情報を確認
   - 入力に `contest_info` がある場合、本編で確認できたなら承認
   - 確認できない場合は `null` にする

## 出力形式

```json
{
  "is_neta": true,
  "confidence": 0.92,
  "format": "manzai",
  "performers": ["太郎", "花子"],
  "segments": [
    {
      "start_sec": 0,
      "end_sec": 245,
      "neta_title": "コンビニのバイト"
    }
  ],
  "setting_tags": ["konbini", "part_timer"],
  "new_tag_proposals": [
    {
      "slug": "convenience_store_customer_service",
      "name": "コンビニの店員対応",
      "category": "theme"
    }
  ],
  "contest": {
    "slug": "m1",
    "year": 2024,
    "round": "final_1st"
  }
}
```

## 注意事項

- **音声・映像の内容を見る**: タイトルや説明だけでなく、動画の実際の内容を参考に判定してください
- **複数言語対応**: 日本語以外の言語を使用していれば、その旨を記録してください
- **メタデータの不正確性**: YouTube の説明文が不正確な場合、実際の内容を優先します
- **外国人芸人**: 日本語で演じられたネタは対象に含めます

## 出力サンプル（不適切な動画）

```json
{
  "is_neta": false,
  "confidence": 1.0,
  "format": null,
  "performers": ["太郎"],
  "segments": [],
  "setting_tags": [],
  "new_tag_proposals": [],
  "contest": null
}
```
