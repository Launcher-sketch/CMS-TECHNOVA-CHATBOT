from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import os

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "technova.json"

def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)

DATA = load_data()

@app.get("/")
def home():
    return render_template("index.html", title=DATA.get("site_title", "CMS TECHNOVA AI Assistant"))

@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip().lower()
    if not message:
        return jsonify(reply="Please type a question.")

    # Match FAQ keywords first.
    for item in DATA.get("faqs", []):
        if any(str(keyword).lower() in message for keyword in item.get("keywords", [])):
            return jsonify(reply=item.get("answer", "I don't have an answer for that yet."))

    # Then match event names.
    for event in DATA.get("events", []):
        name = str(event.get("name", ""))
        if name and name.lower() in message:
            return jsonify(reply=event.get("description", "No description has been added yet."))

    return jsonify(reply=DATA.get(
        "fallback",
        "I couldn't find a confirmed answer. Please contact the TECHNOVA organising team."
    ))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
