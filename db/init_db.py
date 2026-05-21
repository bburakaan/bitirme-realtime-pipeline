from pathlib import Path

from db.connection import get_connection


SCHEMA_PATH = Path(__file__).with_name("init.sql")


def init_database() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    init_database()
    print("Database schema is ready.")


if __name__ == "__main__":
    main()
