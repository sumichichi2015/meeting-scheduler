import json
import os
from typing import Dict, List, Optional

class Database:
    def __init__(self, file_path: str = "data/meetings.json"):
        self.file_path = file_path
        self.data_dir = os.path.dirname(file_path)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists(file_path):
            self._save_data({})
        self.meetings = self._load_data()

    def _load_data(self) -> Dict:
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except:
            return {}

    def _save_data(self, data: Dict) -> None:
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_meeting(self, meeting_id: str) -> Optional[Dict]:
        return self.meetings.get(meeting_id)

    def create_meeting(self, meeting_id: str, meeting_data: Dict) -> Dict:
        self.meetings[meeting_id] = meeting_data
        self._save_data(self.meetings)
        return meeting_data

    def update_meeting(self, meeting_id: str, meeting_data: Dict) -> Optional[Dict]:
        if meeting_id in self.meetings:
            self.meetings[meeting_id] = meeting_data
            self._save_data(self.meetings)
            return meeting_data
        return None

db = Database()
