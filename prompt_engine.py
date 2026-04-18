import os
import anthropic
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

Gunakan semua informasi di atas untuk memberikan respons yang
terasa personal, spesifik, dan relevan dengan kondisi pengguna.
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

    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=messages
    )

    return response.content[0].text
