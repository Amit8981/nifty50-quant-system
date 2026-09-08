"""
Persistent User Feedback and Admin Management Module using SQLite.
Stores user ratings, suggestions, feature requests, and enables admin analysis.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "feedback.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_name TEXT,
            user_email TEXT,
            role TEXT,
            category TEXT NOT NULL,
            rating INTEGER NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'New',
            admin_notes TEXT DEFAULT ''
        )
        """
    )
    conn.commit()

    # Seed sample feedbacks if empty so admin can immediately see analytics
    cursor.execute("SELECT COUNT(*) FROM feedbacks")
    if cursor.fetchone()[0] == 0:
        samples = [
            (
                "2026-08-20 10:30:00",
                "Arjun Sharma",
                "arjun.s@quantdesk.in",
                "Trader",
                "Strategy Improvement",
                5,
                "Bollinger Band mean-reversion with 200 EMA filter performed remarkably well during the 2024 correction. Would love to test an added ADX > 25 filter.",
                "In Review",
                "Agent to test ADX filter integration in next release.",
            ),
            (
                "2026-08-25 14:15:00",
                "Priya Nair",
                "priya.nair@invest.com",
                "Portfolio Manager",
                "Risk Parameter",
                5,
                "The 10% maximum drawdown vs 38% on NIFTY Buy & Hold is exceptional for risk management. Please add an option to trail SL after 1R profit.",
                "Agent Action Needed",
                "Add 1R breakeven trailing stop option.",
            ),
            (
                "2026-09-02 09:45:00",
                "Rohan Mehta",
                "rohan.m@retailalpha.in",
                "Retail Investor",
                "UI / Visualization",
                4,
                "The 'Under The Hood' tab makes the quant logic very transparent. It would be helpful to also show a cumulative trade-by-trade PnL chart.",
                "Implemented",
                "Added in the Equity & Drawdown tab.",
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO feedbacks (timestamp, user_name, user_email, role, category, rating, message, status, admin_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            samples,
        )
        conn.commit()
    conn.close()


def add_feedback(
    user_name: str,
    user_email: str,
    role: str,
    category: str,
    rating: int,
    message: str,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO feedbacks (timestamp, user_name, user_email, role, category, rating, message, status, admin_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'New', '')
        """,
        (now_str, user_name, user_email, role, category, rating, message),
    )
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id


def get_all_feedbacks(category_filter: Optional[str] = None, status_filter: Optional[str] = None) -> pd.DataFrame:
    conn = get_connection()
    query = "SELECT * FROM feedbacks WHERE 1=1"
    params = []
    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)
    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    query += " ORDER BY id DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def update_feedback_status(feedback_id: int, new_status: str, admin_notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE feedbacks
        SET status = ?, admin_notes = ?
        WHERE id = ?
        """,
        (new_status, admin_notes, feedback_id),
    )
    conn.commit()
    conn.close()


def get_feedback_summary() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(rating) FROM feedbacks")
    total_count, avg_rating = cursor.fetchone()

    cursor.execute("SELECT status, COUNT(*) FROM feedbacks GROUP BY status")
    status_counts = dict(cursor.fetchall())

    cursor.execute("SELECT category, COUNT(*) FROM feedbacks GROUP BY category")
    category_counts = dict(cursor.fetchall())

    conn.close()
    return {
        "total_feedbacks": total_count or 0,
        "avg_rating": round(avg_rating or 0.0, 1),
        "status_counts": status_counts,
        "category_counts": category_counts,
    }


# Initialize DB upon module load
init_db()
