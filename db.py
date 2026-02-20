# db.py
import aiosqlite
import asyncio
from typing import List, Dict, Any

DB_PATH = "chat.sqlite3"

# Used resources from ChatGPT generated sample code and modified
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            room TEXT,
            text TEXT,
            role TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        await db.commit()

async def persist_message(user: str, room: str, text: str, role: str = "user"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user,room,text,role) VALUES (?, ?, ?, ?)",
            (user, room, text, role),
        )
        await db.commit()

async def last_messages(room: str, limit: int = 50) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, user, room, text, role, ts FROM messages WHERE room = ? ORDER BY id DESC LIMIT ?",
            (room, limit)
        )
        rows = await cur.fetchall()
        await cur.close()
    # convert to list of dicts, earliest-first
    rows = list(reversed(rows))
    return [
        {"id": r[0], "user": r[1], "room": r[2], "text": r[3], "role": r[4], "ts": r[5]}
        for r in rows
    ]
