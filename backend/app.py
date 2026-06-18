from flask import Flask, jsonify, render_template
from flask_cors import CORS
from auth import auth_bp
from otp import otp_bp
from podcast import podcast_bp
import secrets
import socket


# ---------------- GET LOCAL IP ----------------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def create_app():
    app = Flask(
        __name__,
        template_folder="D:/major project try/ai_podcast_creator/frontend/templates",   # ✅ Correct
        static_folder="D:/major project try/ai_podcast_creator/frontend/static"         # ✅ Correct
    )

    # ---------------- CORS ----------------
    CORS(app)

    # ---------------- CONFIG ----------------
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = secrets.token_hex(32)

    # ---------------- BLUEPRINTS ----------------
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(otp_bp, url_prefix="/otp")
    app.register_blueprint(podcast_bp, url_prefix="/podcast")

    # ---------------- FRONTEND ROUTES ----------------
    @app.route("/")
    def home():
        return render_template("index.html")   # ✅ FIXED

    @app.route("/login")
    def login():
        return render_template("login.html")   # ✅ FIXED
    
    @app.route("/forgot-password")
    def forgot_password():
        return render_template("forgot_password.html")

    @app.route("/register")
    def register():
        return render_template("register.html")   # ✅ FIXED

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")   # ✅ OK
    

    # ---------------- API HEALTH ----------------
    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "online",
            "service": "AI Podcast Creator API"
        })

    # ---------------- TEST ROUTE ----------------
    @app.route("/generate-podcast-test", methods=["POST"])
    def test_generate_podcast():
        return jsonify({
            "status": "success",
            "message": "Frontend ↔ Backend working!"
        })

    # ---------------- ERROR HANDLERS ----------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500

    # ---------------- PRINT URLS ----------------
    local_ip = get_local_ip()
    print("\n🚀 Server running!")
    print(f"👉 Local:   http://127.0.0.1:5000")
    print(f"👉 Network: http://{local_ip}:5000\n")

    return app


# ---------------- RUN ----------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)