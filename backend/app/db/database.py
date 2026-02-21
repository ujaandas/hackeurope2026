import aiosqlite
import json
import os
from app.config import settings

DB_PATH = settings.DATABASE_PATH


async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (datetime('now')),
                filename TEXT NOT NULL,
                language TEXT DEFAULT 'cpp',
                patterns_found INTEGER,
                pattern_details TEXT,
                energy_before REAL,
                energy_after REAL,
                savings_kwh REAL,
                savings_co2_kg REAL,
                savings_eur REAL,
                original_code TEXT,
                optimized_code TEXT,
                chain_of_thought TEXT,
                ai_provider TEXT
            )
        """)
        await db.commit()


async def save_optimization(
    filename: str,
    language: str,
    patterns_found: int,
    pattern_details: list,
    energy_before: float,
    energy_after: float,
    savings_kwh: float,
    savings_co2_kg: float,
    savings_eur: float,
    original_code: str,
    optimized_code: str,
    chain_of_thought: str,
    ai_provider: str,
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO optimizations
            (filename, language, patterns_found, pattern_details, energy_before, energy_after,
             savings_kwh, savings_co2_kg, savings_eur, original_code, optimized_code,
             chain_of_thought, ai_provider)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                filename, language, patterns_found, json.dumps(pattern_details),
                energy_before, energy_after, savings_kwh, savings_co2_kg, savings_eur,
                original_code, optimized_code, chain_of_thought, ai_provider,
            ),
        )
        await db.commit()


async def get_dashboard_data() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT
                COUNT(*) as total_optimizations,
                COALESCE(SUM(savings_kwh), 0) as total_kwh_saved,
                COALESCE(SUM(savings_co2_kg), 0) as total_co2_saved,
                COALESCE(SUM(savings_eur), 0) as total_eur_saved
            FROM optimizations
            """
        )
        row = await cursor.fetchone()
        total_opts = row[0]
        total_kwh = row[1]
        total_co2 = row[2]
        total_eur = row[3]

        # Sustainability score: 0-100 based on total optimizations and savings
        score = min(100, total_opts * 10 + int(total_kwh * 5))

        cursor = await db.execute(
            """
            SELECT id, timestamp, filename, language, patterns_found,
                   energy_before, energy_after, savings_kwh, savings_co2_kg, savings_eur,
                   original_code, optimized_code, chain_of_thought
            FROM optimizations
            ORDER BY timestamp DESC
            LIMIT 50
            """
        )
        rows = await cursor.fetchall()
        history = [
            {
                "id": r[0], "timestamp": r[1], "filename": r[2], "language": r[3],
                "patterns_found": r[4], "energy_before": r[5], "energy_after": r[6],
                "savings_kwh": r[7], "savings_co2_kg": r[8], "savings_eur": r[9],
                "original_code": r[10] or "", "optimized_code": r[11] or "",
                "chain_of_thought": r[12] or "",
            }
            for r in rows
        ]

        return {
            "total_optimizations": total_opts,
            "total_kwh_saved": total_kwh,
            "total_co2_saved": total_co2,
            "total_eur_saved": total_eur,
            "sustainability_score": score,
            "history": history,
        }
