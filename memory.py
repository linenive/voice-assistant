import json
import os
import re
from datetime import datetime

import anthropic
from config import ANTHROPIC_API_KEY, HISTORY_PATH, MODEL

# 장기 기억은 history 폴더 안의 별도 파일에 저장
MEMORY_FILE = os.path.join(HISTORY_PATH, "long_memory.json")

# 메모리 판단용 Claude 클라이언트 (메인 대화와 같은 키/모델 사용)
_memory_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
_MEMORY_MODEL = MODEL


def _load_memories():
    """저장된 장기 기억 전체 불러오기"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            # 파일이 깨졌거나 포맷이 잘못된 경우 새로 시작
            return []
    return []


def _save_memories(memories):
    """장기 기억 전체 저장하기"""
    os.makedirs(HISTORY_PATH, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)


def _tokenize(text: str):
    """아주 단순한 토크나이저 (한글/영문/숫자)"""
    if not text:
        return []
    # 한글, 영문, 숫자만 남기기
    tokens = re.findall(r"[가-힣A-Za-z0-9]+", text.lower())
    # 한 글자짜리 토큰은 버림 (조사 등)
    return [t for t in tokens if len(t) > 1]


def add_memory(content: str, source: str = "user", metadata: dict | None = None):
    """장기 기억 하나 추가하기"""
    memories = _load_memories()
    memories.append(
        {
            "content": content,
            "source": source,
            "metadata": metadata or {},
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    _save_memories(memories)


def _score(query_tokens, memory_tokens):
    """쿼리와 기억 간의 단순 유사도 점수 (공통 토큰 수)"""
    if not query_tokens or not memory_tokens:
        return 0
    return len(set(query_tokens) & set(memory_tokens))


def _call_memory_tool(text: str):
    """
    Claude의 tool calling을 이용해
    '최근 대화를 장기 기억으로 저장할지' 판단 및 요약된 사실 생성.
    - save_long_memory 툴을 호출하면 그 입력을 그대로 add_memory에 저장.
    """
    if not text or not ANTHROPIC_API_KEY:
        return

    tools = [
        {
            "name": "save_long_memory",
            "description": "사용자와의 대화에서, 나중에도 도움이 될 중요한 사실을 장기 기억에 저장합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "저장할 중요한 사실을 한 문장 한국어로 정리한 내용",
                    },
                    "category": {
                        "type": "string",
                        "description": "사실의 유형 (예: 프로필, 좋아하는 것, 가족, 건강, 일정 등)",
                    },
                },
                "required": ["fact"],
            },
        }
    ]

    system_prompt = (
        "너는 음성 어시스턴트의 장기 기억 관리 도우미야.\n"
        "최근 몇 턴의 대화를 보고, 기억하면 좋을 정보들을 save_long_memory 툴을 사용해서 저장해.\n"
        "- 예: 사용자 정보, 좋아하는 음식/취미, 단순히 최근 관심있는 것, 가족 관계, 자주 반복될 일정, 건강 관련 정보 등은 저장.\n"
        "- 저장할 필요가 없으면 툴을 전혀 호출하지 않아도 돼.\n"
        "- 툴을 쓸 때는 fact를 짧고 이해하기 쉽게 한 문장으로 정리해."
    )

    try:
        print("[memory] _call_memory_tool 호출, Claude에게 메모리 판단 요청")
        response = _memory_client.messages.create(
            model=_MEMORY_MODEL,
            max_tokens=64,
            system=system_prompt,
            tools=tools,
            # 메모리 판단용 내부 호출이므로 role은 단순 user 하나만 사용
            messages=[
                {
                    "role": "user",
                    "content": (
                        "다음은 최근 대화 일부야. 이 대화에서 장기 기억으로 저장할 만한 사실이 있다면 "
                        "save_long_memory 툴을 사용해 저장해 줘.\n\n"
                        f"대화:\n{text}"
                    ),
                }
            ],
        )
        print(f"[memory] _call_memory_tool 응답 stop_reason={getattr(response, 'stop_reason', None)}")
        print(f"[memory] _call_memory_tool content 블록 개수={len(getattr(response, 'content', []) )}")
    except Exception as e:
        # 메모리 판단 호출은 실패해도 메인 대화에는 영향이 없도록 조용히 무시
        print(f"[memory] _call_memory_tool 오류: {e}")
        return

    # tool_use 블록만 찾아서 실행 (save_long_memory)
    used_tool = False
    for block in response.content:
        # Anthropic Python SDK v1 기준: block은 Pydantic 모델 객체
        b_type = getattr(block, "type", None)
        b_name = getattr(block, "name", None)
        if b_type == "tool_use" and b_name == "save_long_memory":
            tool_input = getattr(block, "input", None) or {}
            fact = tool_input.get("fact")
            category = tool_input.get("category")
            if fact:
                metadata = {
                    "category": category or "unspecified",
                    "raw_text": text,
                }
                print(f"[memory] save_long_memory 호출됨 -> 저장: {fact!r}, category={metadata['category']}")
                add_memory(fact, source="user", metadata=metadata)
                used_tool = True

    if not used_tool:
        print("[memory] 이번 발화에서는 save_long_memory 툴이 호출되지 않음 (저장 안 함)")


def update_long_term_memory_from_text(text: str):
    """
    최근 대화 내용을 Claude tool calling으로 평가해서,
    중요한 사실이라고 판단될 때만 장기 기억에 저장.
    """
    print(f"[memory] update_long_term_memory_from_text 호출됨: {text!r}")
    _call_memory_tool(text)


def search_memories(query: str, limit: int = 5):
    """
    쿼리와 비슷한 장기 기억들을 점수 순으로 반환.
    - 현재는 토큰 겹치는 개수 기반의 아주 단순한 검색만 사용 (외부 라이브러리 없이 동작).
    """
    memories = _load_memories()
    if not memories or not query:
        return []

    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    scored = []
    for mem in memories:
        m_tokens = _tokenize(mem.get("content", ""))
        score = _score(q_tokens, m_tokens)
        if score > 0:
            scored.append((score, mem))

    # 점수 순으로 정렬 후 상위 limit개만 반환
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:limit]]

