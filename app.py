
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import re
import html

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "data" / "technova.json"


def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def clean_text(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def get_teacher_data(data):
    teachers = [
        {
            "name": "Mr. Abhishek Sharma",
            "event": "AI Innovation Showdown",
            "venue": "AI Lab"
        },
        {
            "name": "Mr. Shantanu Kumar",
            "event": "Robo Soccer",
            "venue": "Turf Area, Cambridge Section"
        },
        {
            "name": "Ms. Noopur Goel",
            "event": "Line Follower",
            "venue": "Robotics Lab"
        },
        {
            "name": "Mr. Shubham Asthana",
            "event": "Obstacle Race / Game Development",
            "venue": "Back Field / AI Lab"
        },
        {
            "name": "Ms. Swaranjali Rawat",
            "event": "Robo War",
            "venue": "Turf Area, Cambridge Section"
        },
        {
            "name": "Mr. Shobhit Kanchan",
            "event": "Boat Race",
            "venue": "Swimming Pool, CMS Aliganj-I"
        },
        {
            "name": "Ms. Manju Rawat",
            "event": "AI and Robotics Quiz",
            "venue": "Computer / AI Lab"
        }
    ]

    return teachers


def make_teacher_table(teachers):
    rows = ""

    for teacher in teachers:
        rows += f"""
        <tr>
            <td>{html.escape(teacher['name'])}</td>
            <td>{html.escape(teacher['event'])}</td>
            <td>{html.escape(teacher['venue'])}</td>
        </tr>
        """

    return f"""
    <div class="table-wrapper">
        <table class="chat-table">
            <thead>
                <tr>
                    <th>Teacher In-Charge</th>
                    <th>Event</th>
                    <th>Venue</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """


def find_answer(message, data):
    message = clean_text(message)

    # Greeting
    greetings = ["hi", "hello", "hey", "good morning",
                 "good afternoon", "good evening"]

    if message in greetings:
        return (
            "Hello! I am the CMS Event Manager Chatbot. "
            "How can I help you today? You can ask me about "
            "TECHNOVA 2026, events, teachers, rules and venues."
        )

    # All teachers
    teacher_words = ["teacher", "teachers", "in charge",
                     "faculty", "coordinator"]

    if (
        any(word in message for word in teacher_words)
        and any(word in message for word in
                ["all", "list", "names", "every", "show"])
    ):
        return make_teacher_table(get_teacher_data(data))

    # Individual teacher
    teachers = get_teacher_data(data)

    for teacher in teachers:
        name_parts = clean_text(teacher["name"]).replace("mr. ", "").replace(
            "ms. ", ""
        )

        if name_parts in message or (
            "abhishek" in message and "abhishek" in name_parts
        ):
            return (
                f"<strong>{html.escape(teacher['name'])}</strong><br>"
                f"Event: {html.escape(teacher['event'])}<br>"
                f"Venue: {html.escape(teacher['venue'])}"
            )

    # FAQs
    for faq in data.get("faqs", []):
        for keyword in faq.get("keywords", []):
            if clean_text(keyword) in message:
                return faq.get("answer", "")

    # Search events
    for event in data.get("events", []):
        keywords = event.get("keywords", [])

        if any(clean_text(keyword) in message for keyword in keywords):
            return (
                f"<strong>{html.escape(event['name'])}</strong><br>"
                f"{html.escape(event.get('description', ''))}"
            )

    # Search event names
    for event in data.get("events", []):
        if clean_text(event["name"]) in message:
            return (
                f"<strong>{html.escape(event['name'])}</strong><br>"
                f"{html.escape(event.get('description', ''))}"
            )

    return data.get(
        "fallback",
        "I couldn't find confirmed information. Please contact the event organisers."
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please enter a question."})

        data = load_data()
        answer = find_answer(user_message, data)

        return jsonify({"reply": answer})

    except Exception as error:
        app.logger.exception("Chat error")
        return jsonify({
            "reply": "Something went wrong. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
