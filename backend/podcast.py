from flask import Blueprint, request, jsonify
from tts import generate_podcast_audio, add_background_music
from db import get_db_connection, close_connection

import os
import jwt
import base64
import requests
import uuid
import traceback

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------
# Blueprint
# ---------------------------------------------------
podcast_bp = Blueprint("podcast", __name__)

# ---------------------------------------------------
# Config
# ---------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

AUDIO_FOLDER = "podcast_audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# ---------------------------------------------------
# Validate ENV
# ---------------------------------------------------
if not JWT_SECRET:
    raise ValueError("JWT_SECRET not found in .env file")


# ---------------------------------------------------
# AUTH FUNCTION
# ---------------------------------------------------
def verify_token(req):
    try:

        auth_header = req.headers.get("Authorization")

        if not auth_header:
            return None, "Authorization header missing"

        if not auth_header.startswith("Bearer "):
            return None, "Invalid authorization format"

        token = auth_header.split(" ")[1]

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload, None

    except jwt.ExpiredSignatureError:
        return None, "Token expired"

    except jwt.InvalidTokenError:
        return None, "Invalid token"

    except Exception:
        return None, "Authentication failed"


# ---------------------------------------------------
# FALLBACK SCRIPT
# ---------------------------------------------------
def fallback_script(topic):

    return f"""
Host: Welcome to today's podcast.
Guest: Thank you for inviting me.

Host: Today we are discussing {topic}. What exactly is it?
Guest: Great question. {topic} is an important concept used in modern technology and business systems.

Host: That's interesting. Can you explain with a real example?
Guest: Sure. Streaming platforms and shopping websites use it to understand user behavior and provide recommendations.

Host: Where else is it used?
Guest: It is used in healthcare, banking, education, social media, and automation systems.

Host: Why is it becoming so popular?
Guest: Because it helps organizations make faster and smarter decisions using data.

Host: Are there any challenges involved?
Guest: Yes, privacy concerns, security issues, and ethical problems are major challenges.

Host: What does the future look like?
Guest: The future is very exciting. More industries are adopting intelligent systems every year.

Host: That's amazing.
Guest: Absolutely. It is one of the fastest-growing fields today.

Host: Thank you for sharing your insights.
Guest: My pleasure.

Host: Thanks everyone for listening. See you next time.
"""


# ---------------------------------------------------
# GENERATE PODCAST SCRIPT
# ---------------------------------------------------
def generate_podcast_script(topic):

    prompt = f"""
You are a professional AI podcast writer.

Generate ONLY a realistic podcast conversation.

TOPIC: {topic}

IMPORTANT RULES:

1. Every line MUST start with ONLY:
Host:
or
Guest:

2. NEVER use:
[Your Name]
[Guest Name]
[Host]
(Host)
(Guest)

3. Do NOT use:
- markdown
- headings
- bullet points
- narration
- stage directions

4. Conversation must sound:
- natural
- human-like
- engaging
- intelligent

5. Minimum 18 exchanges

6. Each response should be:
- short
- conversational
- informative

7. Host should:
- ask questions
- react naturally
- guide conversation

8. Guest should:
- explain concepts clearly
- give real-world examples
- provide insights

EXAMPLE:

Host: Welcome everyone to today's episode.
Guest: Thank you for inviting me.

Host: What is Artificial Intelligence?
Guest: Artificial Intelligence is the simulation of human intelligence using machines and software.

Host: Where is it used in real life?
Guest: It is widely used in healthcare, finance, recommendation systems, and automation.

Now generate the complete podcast conversation.
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )

        if response.status_code != 200:
            return fallback_script(topic)

        result = response.json()

        script = result.get("response", "").strip()

        # Cleanup
        script = script.replace("*", "").strip()

        script = script.replace("[Your Name]", "Host")
        script = script.replace("[Guest's Name]", "Guest")
        script = script.replace("[Guest Name]", "Guest")
        script = script.replace("[Host]", "Host")

        # Validation
        host_count = script.count("Host:")
        guest_count = script.count("Guest:")

        if (
            host_count < 5
            or guest_count < 5
            or len(script.split()) < 80
        ):
            return fallback_script(topic)

        return script

    except Exception:
        return fallback_script(topic)


# ---------------------------------------------------
# PODCAST ROUTE
# ---------------------------------------------------
@podcast_bp.route("/generate", methods=["POST"])
def generate_podcast():

    conn = None
    cursor = None

    try:

        # -------------------------------------------
        # Verify JWT
        # -------------------------------------------
        user, error = verify_token(request)

        if error:
            return jsonify({
                "success": False,
                "error": error
            }), 401

        # -------------------------------------------
        # Get JSON Data
        # -------------------------------------------
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON body"
            }), 400

        title = str(data.get("title", "")).strip()
        category = str(data.get("category", "")).strip()
        topic = str(data.get("topic", "")).strip()

        # -------------------------------------------
        # Validation
        # -------------------------------------------
        if not title:
            return jsonify({
                "success": False,
                "error": "Title is required"
            }), 400

        if not category:
            return jsonify({
                "success": False,
                "error": "Category is required"
            }), 400

        if not topic:
            return jsonify({
                "success": False,
                "error": "Topic is required"
            }), 400

        # -------------------------------------------
        # Generate Script
        # -------------------------------------------
        script = generate_podcast_script(topic)

        # -------------------------------------------
        # Generate Audio
        # -------------------------------------------
        try:

            audio = generate_podcast_audio(script)

        except Exception:

            return jsonify({
                "success": False,
                "error": "Audio generation failed"
            }), 500

        # -------------------------------------------
        # Add Background Music
        # -------------------------------------------
        try:

            audio = add_background_music(audio)

        except Exception:
            pass

        # -------------------------------------------
        # Save Audio File
        # -------------------------------------------
        filename = f"{uuid.uuid4()}.mp3"

        audio_path = os.path.join(
            AUDIO_FOLDER,
            filename
        )

        audio.seek(0)

        with open(audio_path, "wb") as f:
            f.write(audio.read())

        audio.seek(0)

        # -------------------------------------------
        # Save Podcast to MySQL
        # -------------------------------------------
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO podcasts
            (
                user_id,
                title,
                category,
                topic,
                script,
                audio_path
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user["user_id"],
            title,
            category,
            topic,
            script,
            audio_path
        ))

        conn.commit()

        # -------------------------------------------
        # Convert Audio to Base64
        # -------------------------------------------
        audio_base64 = base64.b64encode(
            audio.read()
        ).decode("utf-8")

        # -------------------------------------------
        # Success Response
        # -------------------------------------------
        return jsonify({
            "success": True,
            "title": title,
            "category": category,
            "topic": topic,
            "script": script,
            "audio": audio_base64,
            "mime_type": "audio/mp3"
        })

    except Exception as e:
        print(traceback.format_exc())

        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            close_connection(conn)

# ---------------------------------------------------
# PODCAST HISTORY ROUTE
# ---------------------------------------------------
@podcast_bp.route("/history", methods=["GET"])
def get_podcast_history():

    conn = None
    cursor = None

    try:

        # -------------------------------------------
        # Verify JWT
        # -------------------------------------------
        user, error = verify_token(request)

        if error:
            return jsonify({
                "success": False,
                "error": error
            }), 401

        # -------------------------------------------
        # Get Podcasts from MySQL
        # -------------------------------------------
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                id,
                user_id,
                title,
                category,
                topic,
                script,
                audio_path,
                created_at
            FROM podcasts
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user["user_id"],))

        rows = cursor.fetchall()

        podcasts = []

        for row in rows:
            created_at_val = row[7]
            
            # Handle different datetime formats
            created_at_str = None
            if created_at_val:
                if hasattr(created_at_val, 'isoformat'):
                    created_at_str = created_at_val.isoformat()
                else:
                    created_at_str = str(created_at_val)

            podcasts.append({
                "id": row[0],
                "user_id": row[1],
                "title": row[2],
                "category": row[3],
                "topic": row[4],
                "script": row[5] if row[5] else "",
                "audio_path": row[6],
                "created_at": created_at_str
            })

        # -------------------------------------------
        # Success Response
        # -------------------------------------------
        return jsonify({
            "success": True,
            "podcasts": podcasts
        })

    except Exception as e:
        print(f"History Error: {e}")
        print(traceback.format_exc())

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            close_connection(conn)
# ---------------------------------------------------
# GET AUDIO FILE ROUTE
# ---------------------------------------------------
@podcast_bp.route("/audio/<int:podcast_id>", methods=["GET"])
def get_podcast_audio(podcast_id):

    conn = None
    cursor = None

    try:

        # -------------------------------------------
        # Verify JWT
        # -------------------------------------------
        user, error = verify_token(request)

        if error:
            return jsonify({
                "success": False,
                "error": error
            }), 401

        # -------------------------------------------
        # Get podcast from database
        # -------------------------------------------
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT audio_path
            FROM podcasts
            WHERE id = %s AND user_id = %s
        """, (podcast_id, user["user_id"]))

        row = cursor.fetchone()

        if not row:
            return jsonify({
                "success": False,
                "error": "Podcast not found"
            }), 404

        audio_path = row[0]

        # -------------------------------------------
        # Read audio file
        # -------------------------------------------
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({
                "success": False,
                "error": "Audio file not found"
            }), 404

        with open(audio_path, "rb") as f:
            audio_data = f.read()

        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        # -------------------------------------------
        # Success Response
        # -------------------------------------------
        return jsonify({
            "success": True,
            "audio": audio_base64
        })

    except Exception as e:
        print(traceback.format_exc())

        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            close_connection(conn)
            