import time

import anthropic
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, SYSTEM_PROMPT
from history import get_claude_messages
from memory import search_memories

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _build_system_prompt_with_memory(last_user_text: str) -> str:
    """
    마지막 사용자 발화를 바탕으로 관련 장기 기억을 찾아
    SYSTEM_PROMPT 뒤에 붙여주는 헬퍼 함수.
    """
    system_prompt = SYSTEM_PROMPT

    relevant = search_memories(last_user_text, limit=5)
    if not relevant:
        return system_prompt

    # 장기 기억을 한글 bullet 리스트로 정리
    memory_lines = [f"- {m['content']}" for m in relevant if m.get("content")]
    if not memory_lines:
        return system_prompt

    memory_block = "\n".join(memory_lines)

    system_prompt += (
        "\n\n[사용자에 대한 과거 중요한 정보]\n"
        f"{memory_block}\n\n"
        "위 정보는 예전에 나눈 대화에서 추출한 기억입니다. "
        "정보가 조금 오래되었거나 틀릴 수도 있으니, 필요하면 정중하게 다시 확인해 주세요."
    )
    return system_prompt


def ask_claude(messages):
    """Claude에게 질문하고 답변 받기 (장기 기억을 함께 활용)"""
    # 가장 최근 사용자 발화 찾기
    last_user_text = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_text = m.get("content", "")
            break

    system_prompt = _build_system_prompt_with_memory(last_user_text)

    # 서버 과부하(529 Overloaded) 대비 재시도 로직
    max_retries = 3
    delay = 1.0

    for attempt in range(1, max_retries + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                messages=get_claude_messages(messages),
            )
            return response.content[0].text

        except Exception as e:
            msg = str(e)
            # 529 Overloaded 같은 일시적 장애면 몇 번 재시도
            if "Overloaded" in msg or "529" in msg:
                print(f"Claude 서버 과부하로 재시도 중 ({attempt}/{max_retries})...: {e}")
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue

            print(f"Claude API 오류: {e}")
            return "죄송해요, 잠시 문제가 생겼어요. 다시 말씀해주세요."

