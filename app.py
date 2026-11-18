
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import os
import re

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "technova.json"


def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def contains_any(message, words):
    return any(
        str(word).lower() in message
        for word in words if word
    )


def get_teacher(event):
    description = event.get("description", "")
    match = re.search(
        r"Teacher:\s*([^.\n]+)",
        description,
        re.IGNORECASE
    )
    return match.group(1).strip() if match else "Not specified"


def teacher_table(events):
    rows = [
        "| TECHNOVA Event | Teacher In-charge |",
        "|---|---|"
    ]

    for event in events:
        rows.append(
            f"| {event.get('name', 'Unnamed Event')} | "
            f"{get_teacher(event)} |"
        )

    return "\n".join(rows)


def find_matching_event(message, events):
    matches = []

    for event in events:
        terms = [event.get("name", "")] + event.get("keywords", [])

        for term in terms:
            term = str(term).lower().strip()

            if len(term) >= 4 and term in message:
                matches.append((len(term), event))
                break

    if not matches:
        return None

    matches.sort(key=lambda item: item[0], reverse=True)
    return matches[0][1]


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
    events = data.get("events", [])

    # 1. Teacher-related questions get priority.
    teacher_words = [
        "teacher", "teachers", "incharge",
        "in-charge", "in charge", "faculty",
        "who handles", "who is handling",
        "responsible teacher"
    ]

    is_teacher_question = contains_any(message, teacher_words)

    if is_teacher_question:
        # Questions asking for the complete teacher list.
        all_teacher_words = [
            "all", "every", "list", "names",
            "category", "categories", "everyone",
            "all events", "all teachers"
        ]

        if contains_any(message, all_teacher_words):
            return jsonify(
                reply=(
                    "Here is the complete TECHNOVA 2026 "
                    "event-wise teacher list:\n\n"
                    + teacher_table(events)
                )
            )

        # Try to identify one particular event.
        matched_event = find_matching_event(message, events)

        if matched_event:
            return jsonify(
                reply=(
                    f"**{matched_event.get('name')}**\n\n"
                    f"Teacher In-charge: **{get_teacher(matched_event)}**"
                )
            )

        # General teacher question: show the complete list.
        return jsonify(
            reply=(
                "Here are the confirmed TECHNOVA 2026 "
                "event-wise teacher assignments:\n\n"
                + teacher_table(events)
            )
        )

    # 2. Match a named event.
    matched_event = find_matching_event(message, events)

    if matched_event:
        return jsonify(
            reply=matched_event.get("description")
            or "No confirmed details have been added for this event yet."
        )

    # 3. Match a category.
    for category in data.get("categories", []):
        if contains_any(
            message,
            [category.get("name", "")] + category.get("keywords", [])
        ):
            matching = [
                event for event in events
                if event.get("category") == category.get("id")
            ]

            if matching:
                names = "\n".join(
                    "• " + event.get("name", "Unnamed event")
                    for event in matching
                )

                return jsonify(
                    reply=(
                        f"{category.get('name')}:\n"
                        f"{names}\n"
                        "Ask me about any listed event."
                    )
                )

            return jsonify(
                reply=(
                    f"{category.get('name')} is available as a category, "
                    "but confirmed event details have not been added yet. "
                    "Please check the latest CMS notice or ask your school coordinator."
                )
            )

    # 4. General FAQ matching.
    for item in data.get("faqs", []):
        if contains_any(message, item.get("keywords", [])):
            return jsonify(
                reply=item.get("answer", "I don't have an answer for that yet.")
            )

    # 5. Fallback.
    return jsonify(
        reply=data.get(
            "fallback",
            "I couldn't find confirmed information about that."
        )
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
