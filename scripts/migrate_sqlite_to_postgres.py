import os
import sqlite3
from datetime import datetime

import psycopg2


SQLITE_PATH = os.getenv("SQLITE_PATH", "maasuraksha.db")
DATABASE_URL = os.getenv("DATABASE_URL")
PGSSLMODE = os.getenv("PGSSLMODE", "require")


def normalize_timestamp(value):
    if not value:
        return datetime.utcnow()
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.utcnow()


def require_env():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is required to migrate data to Neon/PostgreSQL.")
    if not os.path.exists(SQLITE_PATH):
        raise RuntimeError(f"SQLite file not found: {SQLITE_PATH}")


def create_tables(pg_cur):
    pg_cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            age DOUBLE PRECISION,
            gestational_month INTEGER,
            blood_pressure TEXT,
            hemoglobin DOUBLE PRECISION,
            complications TEXT,
            risk_level TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    pg_cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_tracker (
            id SERIAL PRIMARY KEY,
            mood TEXT,
            water_intake INTEGER,
            sleep_hours DOUBLE PRECISION,
            symptoms TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    pg_cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )


def migrate_users(sqlite_cur, pg_cur):
    sqlite_cur.execute("SELECT username, password, role FROM users")
    rows = sqlite_cur.fetchall()
    for row in rows:
        pg_cur.execute(
            """
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            """,
            (row[0], row[1], row[2]),
        )


def migrate_predictions(sqlite_cur, pg_cur):
    sqlite_cur.execute(
        """
        SELECT age, gestational_month, blood_pressure, hemoglobin, complications, risk_level, timestamp
        FROM predictions
        """
    )
    rows = sqlite_cur.fetchall()
    for row in rows:
        pg_cur.execute(
            """
            INSERT INTO predictions
            (age, gestational_month, blood_pressure, hemoglobin, complications, risk_level, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                normalize_timestamp(row[6]),
            ),
        )


def migrate_tracker(sqlite_cur, pg_cur):
    sqlite_cur.execute(
        """
        SELECT mood, water_intake, sleep_hours, symptoms, timestamp
        FROM daily_tracker
        """
    )
    rows = sqlite_cur.fetchall()
    for row in rows:
        pg_cur.execute(
            """
            INSERT INTO daily_tracker
            (mood, water_intake, sleep_hours, symptoms, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                row[0],
                row[1],
                row[2],
                row[3],
                normalize_timestamp(row[4]),
            ),
        )


def main():
    require_env()
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_cur = sqlite_conn.cursor()

    pg_conn = psycopg2.connect(DATABASE_URL, sslmode=PGSSLMODE)
    pg_cur = pg_conn.cursor()

    try:
        create_tables(pg_cur)
        migrate_users(sqlite_cur, pg_cur)
        migrate_predictions(sqlite_cur, pg_cur)
        migrate_tracker(sqlite_cur, pg_cur)
        pg_conn.commit()
        print("Migration completed successfully.")
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        pg_cur.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
