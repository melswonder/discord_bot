"""データベース接続と操作"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.getenv('DATABASE_URL')


@contextmanager
def get_connection():
    """データベース接続を取得"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """テーブルを初期化"""
    if not DATABASE_URL:
        print("DATABASE_URL が設定されていません。データベース機能は無効です。")
        return False

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS quiz_stats (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    correct_count INT DEFAULT 0,
                    total_count INT DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    print("データベースを初期化しました")
    return True


def record_answer(user_id: int, username: str, is_correct: bool):
    """回答を記録"""
    if not DATABASE_URL:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO quiz_stats (user_id, username, correct_count, total_count, updated_at)
                VALUES (%s, %s, %s, 1, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    correct_count = quiz_stats.correct_count + %s,
                    total_count = quiz_stats.total_count + 1,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, username, 1 if is_correct else 0, 1 if is_correct else 0))


def get_user_stats(user_id: int):
    """ユーザーの統計を取得"""
    if not DATABASE_URL:
        return None

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT username, correct_count, total_count
                FROM quiz_stats
                WHERE user_id = %s
            """, (user_id,))
            return cur.fetchone()


def get_ranking(limit: int = 10):
    """正答率ランキングを取得"""
    if not DATABASE_URL:
        return []

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT username, correct_count, total_count,
                       ROUND(correct_count * 100.0 / NULLIF(total_count, 0), 1) as rate
                FROM quiz_stats
                WHERE total_count >= 5
                ORDER BY rate DESC, total_count DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()
