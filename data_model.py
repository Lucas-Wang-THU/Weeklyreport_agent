import json
import os
from config import DATA_FILE

class PlanManager:
    def __init__(self):
        self.filename = DATA_FILE
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._default_structure()
        return self._default_structure()

    def _default_structure(self):
        return {
            # 结构升级：items 列表包含 { "title":Str, "status":Bool, "result":Str, "images":List[Str] }
            "weekly_items": [],
            "next_week_plan": [],
            "long_term_goals": "",
            "significance": "",
            "literature": "",
            "others": "暂无"
        }

    def save_data(self, data):
        self.data = data
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)