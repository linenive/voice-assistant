import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "안녕하세요! 테스트입니다."}
    ]
)

print(response.content[0].text)