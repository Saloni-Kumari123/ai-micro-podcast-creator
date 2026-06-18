from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection, close_connection
import jwt  # ✅ Correct PyJWT import
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

auth_bp = Blueprint('auth', __name__)

# ---------------- JWT CONFIG ----------------
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # 1 hour

if not JWT_SECRET:
    raise ValueError("❌ JWT_SECRET not set in .env file")


# ---------------- REGISTER ----------------
@auth_bp.route('/register', methods=['POST'])
def register():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input provided"}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not username or not email or not password:
            return jsonify({"error": "All fields are required"}), 400
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check existing user
        cursor.execute(
            "SELECT id FROM users WHERE email=%s OR username=%s",
            (email, username)
        )
        if cursor.fetchone():
            return jsonify({"error": "User already exists"}), 400

        password_hash = generate_password_hash(password)

        # Insert user
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, NOW())",
            (username, email, password_hash)
        )
        conn.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print("❌ ERROR (register):", str(e))
        return jsonify({"error": "Server error"}), 500

    finally:
        close_connection(conn, cursor)


# ---------------- LOGIN ----------------
@auth_bp.route('/login', methods=['POST'])
def login():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input provided"}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # ✅ JWT Token
        payload = {
    "user_id": user['id'],
    "username": user['username'],
    "email": user['email'],
    "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
}

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        # PyJWT 2.x returns str, so decode only if bytes
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email']
            }
        }), 200

    except Exception as e:
        print("❌ ERROR (login):", str(e))
        return jsonify({"error": "Server error"}), 500

    finally:
        close_connection(conn, cursor)