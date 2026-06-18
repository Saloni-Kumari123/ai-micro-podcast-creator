import mysql.connector
from mysql.connector import pooling, Error
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------- ENV VARIABLES ----------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "ai_podcast"),
    "autocommit": True
}

# ---------------- CONNECTION POOL ----------------
db_pool = None

try:
    db_pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        pool_reset_session=True,
        **DB_CONFIG
    )
    print("✅ MySQL Connection Pool Created Successfully")

except Error as e:
    print("❌ DB Pool Error:", str(e))


# ---------------- GET CONNECTION ----------------
def get_db_connection():
    try:
        if not db_pool:
            raise Exception("Connection pool not initialized")

        conn = db_pool.get_connection()

        if conn.is_connected():
            return conn
        else:
            print("⚠️ Connection inactive")
            return None

    except Error as e:
        print("❌ Database Connection Error:", str(e))
        return None


# ---------------- CLOSE CONNECTION SAFELY ----------------
def close_connection(conn=None, cursor=None):
    try:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()

    except Error as e:
        print("❌ Error closing connection:", str(e))


# ---------------- TEST CONNECTION ----------------
def test_connection():
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            print("✅ Database Connected Successfully")
        else:
            print("❌ Failed to connect to DB")
    except Exception as e:
        print("❌ Test Connection Error:", str(e))
    finally:
        close_connection(conn)