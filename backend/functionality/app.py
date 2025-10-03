# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from connector import Connector

app = Flask(__name__)
CORS(app)

@app.get("/")
def home():
    return jsonify({"message": "Flask API is running", "routes": ["/health"]})

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

# Optional: avoid favicon 404s
@app.get("/favicon.ico")
def favicon():
    return ("", 204)

@app.route("/api/events")
def get_events():
    con = Connector()
    data = con.extract_event_details()
    results = [{"title": data[1], "about": data[2]} for row in data]
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)


