from flask import Blueprint, request, jsonify
import random
import smtplib
import os
import time
from email.mime.text import MIMEText
from db import get_db_connection, close_connection
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()
otp_bp = Blueprint('otp', __name__)

# ---------------- OTP STORE ----------------
# {email: {"otp": "123456", "time": timestamp, "verified": False}}
otp_store = {}

OTP_EXPIRY = 300  # 5 minutes


# ---------------- SEND EMAIL ----------------
def send_email(to_email, otp_code):
    try:
        sender_email = os.getenv("EMAIL_USER")
        sender_password = os.getenv("EMAIL_PASS")

        msg = MIMEText(f"Your AI Podcast OTP is: {otp_code}")
        msg['Subject'] = "AI Podcast - OTP Verification"
        msg['From'] = sender_email
        msg['To'] = to_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        print("❌ Email Error:", str(e))
        return False


# ---------------- FORGOT PASSWORD ----------------
@otp_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        email = data.get('email', '').strip()

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Check DB
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if not cursor.fetchone():
            return jsonify({"error": "Email not found"}), 404

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))

        otp_store[email] = {
            "otp": otp_code,
            "time": time.time(),
            "verified": False
        }

        # Send email
        if send_email(email, otp_code):
            return jsonify({"message": "OTP sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send email"}), 500

    except Exception as e:
        print("❌ ERROR (forgot-password):", str(e))
        return jsonify({"error": "Server error"}), 500

    finally:
        close_connection(conn, cursor)


# ---------------- VERIFY OTP ----------------
@otp_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        user_otp = data.get('otp', '').strip()

        if email not in otp_store:
            return jsonify({"error": "Request OTP first"}), 400

        stored = otp_store[email]

        # Expiry check
        if time.time() - stored["time"] > OTP_EXPIRY:
            otp_store.pop(email)
            return jsonify({"error": "OTP expired"}), 400

        if user_otp == stored["otp"]:
            otp_store[email]["verified"] = True
            return jsonify({"message": "OTP verified"}), 200

        return jsonify({"error": "Invalid OTP"}), 400

    except Exception as e:
        print("❌ ERROR (verify-otp):", str(e))
        return jsonify({"error": "Server error"}), 500


# ---------------- RESET PASSWORD ----------------
@otp_bp.route('/reset-password', methods=['POST'])
def reset_password():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        new_password = data.get('new_password', '').strip()

        if not email or not new_password:
            return jsonify({"error": "All fields required"}), 400

        if email not in otp_store or not otp_store[email]["verified"]:
            return jsonify({"error": "OTP not verified"}), 403

        if len(new_password) < 6:
            return jsonify({"error": "Password too short"}), 400

        hashed_pw = generate_password_hash(new_password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE email=%s",
            (hashed_pw, email)
        )

        conn.commit()

        # Cleanup
        otp_store.pop(email)

        return jsonify({"message": "Password updated successfully"}), 200

    except Exception as e:
        print("❌ ERROR (reset-password):", str(e))
        return jsonify({"error": "Server error"}), 500

    finally:
        close_connection(conn, cursor)