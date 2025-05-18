from typing import List

CRISIS_KEYWORDS: List[str] = [
    "suicidal","suicide", "kill", "death", "die", "hurt", "pain", "sad", "cry",
    "depressed", "depression", "anxiety", "panic", "overdose", "self-harm", "self-injury",
    "can't go on", "can't take it anymore", "can't do this", "can't handle it",
    "can't cope", "can't live like this", "can't keep going", "can't keep living",
]

SAFETY_MESSAGE = (
    "It sounds like you're going through a really tough time. I want to make sure you're safe. Can you tell me if you're in immediate danger or if you're thinking about hurting yourself?"
    "I care about your well-being, and it's important to talk to someone who can help. Have you considered reaching out to a mental health professional or a crisis hotline?"
    "You are not alone in this, and there are people who want to support you. Please let me know how I can assist you further."
    "Pleasse consider reaching out to a mental health professional or a crisis hotline. They can provide you with the support you need."
    "📞 **SA Emergency Line:** 10111 (SAPS)\n"
    "💙 You matter."
)

def contains_crisis_keywords(user_query: str) -> bool:
    text_lower = user_query.lower()
    return any(keyword in text_lower for keyword in CRISIS_KEYWORDS)