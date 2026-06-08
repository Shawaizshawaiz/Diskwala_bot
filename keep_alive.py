from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route("/")
def home():
    """Health check endpoint — used by UptimeRobot to keep Replit alive."""
    return "✅ Terabox Bot is running!"


def run():
    """Run Flask on port 8080."""
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    """Start the Flask server in a background thread."""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("[keep_alive] Flask server started on port 8080")
