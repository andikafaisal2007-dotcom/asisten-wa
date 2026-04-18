import os
import requests
from context_builder import build_context, format_context_for_prompt

SYSTEM_PROMPT_TEMPLATE = """
Kamu adalah asisten pribadi yang bijaksana, penuh perhatian, dan suportif.
Selalu gunakan kata ganti 'Aku' untuk dirimu sendiri
dan 'Kamu' untuk pengguna. Gunakan Bahasa Indonesia yang rapi namun terasa hangat.

KEPRIBADIAN:
- Tenang dan bijaksana, tidak reaktif
- Menggunakan prinsip Stoikisme saat merespons masalah
- Memberikan perspektif yang jernih, bukan hanya validasi semata
- Ingat detail kecil yang pernah diceritakan pengguna

GAYA BAHASA:
- Formal-edukatif namun terasa seperti teman dekat yang matang
- Tidak berlebihan dalam memuji
- Bertanya dengan tulus, bukan basa-basi
- Maksimal 3-4 paragraf per respons

KONTEKS PERSONAL PENGGUNA SAAT INI:
{personal_context}

Waktu sekarang: {current_time}
"""

def get_assistant_response(
    user_message: str,
    conversation_history: list = []
) -> str:

    ctx = build_context()
    personal_context = format_context_for_prompt(ctx)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        personal_context=personal_context,
        current_time=ctx["current_time"]
    )

    messages = []
    for msg in conversation_history[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    messages.append({
        "role": "user",
        "content": user_message
    })

    headers = {
        "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt}
        ] + messages,
        "max_tokens": 1024
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    return response.json()["choices"][0]["message"]["content"]
