def build_recent_dialog(messages, turns: int = 3) -> str:
    """최근 user/assistant 각각 turns턴 정도의 대화를 문자열로 묶어서 반환"""
    if not messages:
        return ""

    # user/assistant 페어를 고려해서 2 * turns 만큼만 사용
    recent = messages[-2 * turns :]
    lines = []
    for m in recent:
        role = m.get("role")
        speaker = "사용자" if role == "user" else "어시스턴트"
        lines.append(f"{speaker}: {m.get('content', '')}")
    return "\n".join(lines)

