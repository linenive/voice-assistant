import anthropic
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, SYSTEM_PROMPT
from history import get_claude_messages

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def ask_claude(messages):
    """Claude에게 질문하고 답변 받기"""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=get_claude_messages(messages)
        )
        return response.content[0].text

    except Exception as e:
        print(f"Claude API 오류: {e}")
        return "죄송해요, 잠시 문제가 생겼어요. 다시 말씀해주세요."
