import json
import os
from datetime import datetime
from config import HISTORY_PATH

def get_history_path():
    """오늘 날짜로 파일 경로 생성"""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(HISTORY_PATH, f"history_{today}.json")

def load_history():
    """오늘의 대화 기록 불러오기"""
    path = get_history_path()
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(messages):
    """오늘의 대화 기록 저장하기"""
    path = get_history_path()
    
    # 폴더 없으면 생성
    os.makedirs(HISTORY_PATH, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def add_message(messages, role, content):
    """대화 기록에 메시지 추가"""
    messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_history(messages)
    return messages

def get_claude_messages(messages):
    """Claude API 형식으로 변환 (timestamp 제거)"""
    return [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]
