import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Vi gemmer events i en liste i hukommelsen. Når API'en genstarter er alt væk,
# men det er fint til opgaven.
events = [
    {
        "id": 1,
        "title": "Quizaften",
        "date": "2026-11-13",
        "capacity": 3,
        "participants": ["Anna", "Bo"],
    },
    {
        "id": 2,
        "title": "Beerpong-turnering",
        "date": "2026-11-20",
        "capacity": 8,
        "participants": [],
    },
    {
        "id": 3,
        "title": "Brætspilsaften",
        "date": "2026-11-27",
        "capacity": 12,
        "participants": ["Clara"],
    },
]

# Tæller op hver gang vi opretter et nyt event, så id'er ikke går igen
next_id = 4


def find_event(event_id):
    for e in events:
        if e["id"] == event_id:
            return e
    return None


@app.get("/events")
def list_events():
    return jsonify(events), 200


@app.get("/events/<int:event_id>")
def get_event(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": "Event findes ikke"}), 404
    return jsonify(event), 200


@app.post("/events")
def create_event():
    global next_id
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    date = data.get("date")
    capacity = data.get("capacity")

    # Alle tre felter skal være der
    if not title or not date or capacity is None:
        return jsonify({"error": "title, date og capacity er påkrævet"}), 400

    # bool er teknisk set en int i Python, så vi tjekker også for det
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity <= 0:
        return jsonify({"error": "capacity skal være et positivt heltal"}), 400

    event = {
        "id": next_id,
        "title": title,
        "date": date,
        "capacity": capacity,
        "participants": [],
    }
    next_id += 1
    events.append(event)
    return jsonify(event), 201


@app.delete("/events/<int:event_id>")
def delete_event(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": "Event findes ikke"}), 404
    events.remove(event)
    return "", 204


@app.post("/events/<int:event_id>/signups")
def signup(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": "Event findes ikke"}), 404

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name er påkrævet"}), 400

    # Samme person må ikke stå på listen to gange
    if name in event["participants"]:
        return jsonify({"error": f"{name} er allerede tilmeldt"}), 409

    # Stop hvis der ikke er flere pladser
    if len(event["participants"]) >= event["capacity"]:
        return jsonify({"error": "Eventet er fuldt"}), 409

    event["participants"].append(name)
    return jsonify(event), 201


@app.delete("/events/<int:event_id>/signups/<name>")
def cancel_signup(event_id, name):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": "Event findes ikke"}), 404

    if name not in event["participants"]:
        return jsonify({"error": "Tilmeldingen findes ikke"}), 404

    event["participants"].remove(name)
    return "", 204


if __name__ == "__main__":
    # Lokalt binder vi til 127.0.0.1 så vi ikke lytter på hele netværket.
    # I Docker sætter compose HOST=0.0.0.0 så containeren kan nås udefra.
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=5000, debug=True)
