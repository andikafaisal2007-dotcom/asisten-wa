import os
import sqlite3
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from database import init_database
from prompt_engine import get_assistant_response

app = Flask(__name__)
init_database()

def get_recent_history(limit: int = 10) -> list:
    conn = sqlite3.connect("assistant.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT role, content FROM conversations
        ORDER BY timestamp DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def save_message(role: str, content: str):
    conn = sqlite3.connect("assistant.db")
    conn.execute(
        "INSERT INTO conversations (role, content) VALUES (?, ?)",
        (role, content)
    )
    conn.commit()
    conn.close()


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()

    save_message("user", incoming_msg)

    history = get_recent_history()

    reply = get_assistant_response(incoming_msg, history)

    save_message("assistant", reply)

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
