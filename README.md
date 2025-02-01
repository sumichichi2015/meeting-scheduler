# 会議調整アプリケーション

シンプルな会議日程調整Webアプリケーション。

## 開発環境のセットアップ

### 必要条件
- Python 3.8以上
- Node.js 16以上
- npm 8以上

### バックエンド環境構築
```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate

# 依存パッケージのインストール
pip3 install -r requirements.txt

# 開発サーバーの起動
uvicorn main:app --reload
```

### フロントエンド環境構築
```bash
# 依存パッケージのインストール
cd frontend
npm install

# 開発サーバーの起動
npm run dev
```

## プロジェクト構造
```
.
├── README.md
├── docs/
│   ├── SPEC.md
│   └── spec.yaml
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
└── frontend/
    ├── package.json
    ├── index.html
    └── src/
        ├── App.vue
        ├── main.js
        └── components/
```

## 仕様書
詳細な仕様については、[SPEC.md](docs/SPEC.md)を参照してください。
