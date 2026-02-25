import os
from datetime import datetime

# OpenRouter / OpenAI API 配置
OPENROUTER_API_KEY = "****" # 请在此处填入您的OpenRouter Key
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "arcee-ai/trinity-large-preview:free" # 或其他支持的模型

# 用户信息
USER_NAME = "王骄阳"

# 路径配置
# 自动获取本周日的日期用于文件夹命名，格式如 260119 (YYMMDD)
current_date = datetime.now()
date_str = current_date.strftime("%y%m%d")
base_drive = "D:\\" if os.name == 'nt' else os.path.expanduser("~/") # 兼容非D盘环境
REPORT_BASE_DIR = os.path.join(base_drive, "周报")
REPORT_WEEKLY_DIR = os.path.join(REPORT_BASE_DIR, date_str)

# 确保目录存在
if not os.path.exists(REPORT_WEEKLY_DIR):
    try:
        os.makedirs(REPORT_WEEKLY_DIR)
    except Exception as e:
        print(f"创建目录失败: {e}")

FILE_NAME = f"{USER_NAME}_{date_str}周报.docx"
FULL_REPORT_PATH = os.path.join(REPORT_WEEKLY_DIR, FILE_NAME)
DATA_FILE = "plan_data.json" # 本地存储计划数据