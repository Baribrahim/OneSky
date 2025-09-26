# app.py
from flask import Flask, jsonify
from flask_cors import CORS

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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
