from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import os

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "technova.json"

def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)

def contains_any(message, words):
    return any(str(word).lower() in message for word in words if word)

@app.get("/")
def home():
    data = load_data()
    return render_template(
        "index.html",
        title=data.get("site_title", "CMS Events Assistant"),
        categories=data.get("categories", [])
    )

@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip().lower()
    if not message:
        return jsonify(reply="Please type a question.")

    data = load_data()

    # Match a named event first, including its description and category.
    for event in data.get("events", []):
        searchable = [event.get("name", "")] + event.get("keywords", [])
        if contains_any(message, searchable):
            return jsonify(reply=event.get("description") or "No confirmed details have been added for this event yet.")

    # Category-specific response: available data wins over the coming-soon label.
    for category in data.get("categories", []):
        if contains_any(message, [category.get("name", "")] + category.get("keywords", [])):
            matching = [e for e in data.get("events", []) if e.get("category") == category.get("id")]
            if matching:
                names = "\\n".join("• " + e.get("name", "Unnamed event") for e in matching)
                return jsonify(reply=f"{category.get('name')}:\\n{names}\\nAsk me about any listed event.")
            if category.get("id") == "technova":
                return jsonify(reply="TECHNOVA 2026 is listed in the CMS Events Assistant. Detailed competition information must be added from the official brochure before I can give confirmed answers.")
            return jsonify(reply=f"{category.get('name')} is available as a category, but confirmed event details have not been added yet. Please check the latest CMS notice or ask your school coordinator.")

    # General FAQ matching.
    for item in data.get("faqs", []):
        if contains_any(message, item.get("keywords", [])):
            return jsonify(reply=item.get("answer", "I don't have an answer for that yet."))

    return jsonify(reply=data.get("fallback", "I couldn't find a confirmed answer. Please check the latest official CMS notice."))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
