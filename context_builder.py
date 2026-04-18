import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any

def build_context(db_path: str = "assistant.db") -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT key, value, category FROM user_profile ORDER BY category")
    profile_rows = cur.fetchall()
    profile = {row['key']: row['value'] for row in profile_rows}

    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cur.execute("""
        SELECT activity, category, logged_at, duration_min, notes, mood_score
        FROM routines
        WHERE logged_at >= ?
        ORDER BY logged_at DESC
        LIMIT 10
    """, (week_ago,))
    recent_routines = [dict(row) for row in cur.fetchall()]

    now = datetime.now().isoformat()
    soon = (datetime.now() + timedelta(hours=48)).isoformat()
    cur.execute("""
        SELECT title, scheduled_at, importance, notes
        FROM agendas
        WHERE scheduled_at BETWEEN ? AND ?
        ORDER BY scheduled_at ASC
    """, (now, soon))
    upcoming_agendas = [dict(row) for row in cur.fetchall()]

    cur.execute("""
        SELECT topic, context, followup_at
        FROM checkpoints
        WHERE resolved = 0
        ORDER BY followup_at ASC
        LIMIT 5
    """)
    pending_checkpoints = [dict(row) for row in cur.fetchall()]

    yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
    cur.execute("""
        SELECT role, content, timestamp
        FROM conversations
        WHERE timestamp >= ?
        ORDER BY timestamp ASC
        LIMIT 20
    """, (yesterday,))
    recent_convo = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        "profile": profile,
        "recent_routines": recent_routines,
        "upcoming_agendas": upcoming_agendas,
        "pending_checkpoints": pending_checkpoints,
        "recent_conversations": recent_convo,
        "current_time": datetime.now().strftime("%A, %d %B %Y pukul %H:%M"),
    }


def format_context_for_prompt(ctx: Dict[str, Any]) -> str:
    lines = []

    if ctx["profile"]:
        lines.append("=== PROFIL PENGGUNA ===")
        for k, v in ctx["profile"].items():
            lines.append(f"• {k}: {v}")

    if ctx["recent_routines"]:
        lines.append("\n=== RUTINITAS 7 HARI TERAKHIR ===")
        for r in ctx["recent_routines"]:
            lines.append(
                f"• {r['activity']} ({r['category']}) — {r['duration_min']} menit"
                f"  Catatan: {r['notes'] or '-'}  Mood: {r['mood_score']}/5"
            )

    if ctx["upcoming_agendas"]:
        lines.append("\n=== AGENDA MENDATANG ===")
        for a in ctx["upcoming_agendas"]:
            lines.append(f"• [{a['importance'].upper()}] {a['title']} — {a['scheduled_at']}")

    if ctx["pending_checkpoints"]:
        lines.append("\n=== TOPIK YANG PERLU DITINDAKLANJUTI ===")
        for c in ctx["pending_checkpoints"]:
            lines.append(f"• {c['topic']} — konteks: {c['context']}")

    return "\n".join(lines)
