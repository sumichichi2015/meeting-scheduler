from fastapi.testclient import TestClient
import pytest
from ..main import app

def test_create_meeting(client):
    response = client.post(
        "/meetings/",
        json={
            "title": "テスト会議",
            "description": "テスト用の会議です",
            "date_options": ["2025-02-03T10:00:00", "2025-02-04T15:00:00"]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "テスト会議"
    assert len(data["date_options"]) == 2

def test_get_meeting(client):
    # 会議を作成
    create_response = client.post(
        "/meetings/",
        json={
            "title": "取得テスト会議",
            "description": "取得テスト用の会議です",
            "date_options": ["2025-02-03T10:00:00"]
        }
    )
    meeting_id = create_response.json()["id"]

    # 作成した会議を取得
    response = client.get(f"/meetings/{meeting_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "取得テスト会議"

def test_add_participant(client):
    # 会議を作成
    create_response = client.post(
        "/meetings/",
        json={
            "title": "参加者テスト会議",
            "description": "参加者追加テスト用の会議です",
            "date_options": ["2025-02-03T10:00:00"]
        }
    )
    meeting_id = create_response.json()["id"]

    # 参加者を追加
    response = client.post(
        f"/meetings/{meeting_id}/participants",
        json={
            "name": "テスト太郎",
            "availability": [{"date": "2025-02-03T10:00:00", "available": True}]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "テスト太郎"
    assert len(data["availability"]) == 1
