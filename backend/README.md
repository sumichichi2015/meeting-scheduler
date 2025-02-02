# 会議調整アプリ バックエンド

## セットアップ手順

1. 必要なパッケージをインストール:
```bash
pip3 install -r requirements.txt
```

2. サーバーの起動:
```bash
cd backend
python3 -m uvicorn app.main:app --reload --port 3002
```

## 利用可能なAPI

### 1. 会議の作成
- エンドポイント: POST /meetings
- データ例:
```json
{
  "name": "週次ミーティング",
  "organizer": "山田太郎",
  "dates": ["2025-02-01", "2025-02-02"],
  "time_slots": {
    "2025-02-01": ["09:00", "09:30", "10:00"],
    "2025-02-02": ["14:00", "14:30", "15:00"]
  }
}
```

### 2. 会議の詳細取得
- エンドポイント: GET /meetings/{meeting_id}

### 3. 参加者の追加
- エンドポイント: POST /meetings/{meeting_id}/participants
- データ例:
```json
{
  "name": "田中一郎",
  "availability": {
    "2025-02-01": {
      "09:00": "○",
      "09:30": "△"
    }
  },
  "comment": "午前中であれば参加可能です"
}
```

### 4. 参加者一覧の取得
- エンドポイント: GET /meetings/{meeting_id}/participants
