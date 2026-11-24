import os
import random
from typing import Optional
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v4.0.0")

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
}

clients_db = [
    {
        "id": 1,
        "name": "Aarav Sharma",
        "age": 29,
        "weight": 78.5,
        "program": "Muscle Gain",
        "calories": 2400,
        "target_weight": 82.0,
        "membership_status": "Active",
        "adherence": 85,
    }
]

workouts_db = [
    {
        "id": 1,
        "client_name": "Aarav Sharma",
        "workout_type": "Strength",
        "duration_min": 60,
        "notes": "Push day baseline",
    }
]

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>ACEest Fitness & Gym ({{ version }})</title>
  <style>
    body { font-family: Arial, sans-serif; background: #1a1a1a; color: #f5f5f5; margin: 2rem; }
    h1 { color: #d4af37; }
    .badge { background: #d4af37; color: #111; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .card { background: #262626; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <h1>ACEest Fitness & Gym <span class="badge">{{ version }}</span></h1>
  <div class="card">
    <h2>Active Clients ({{ clients|length }})</h2>
    <ul>
      {% for c in clients %}
        <li><strong>{{ c.name }}</strong> — Program: {{ c.program }} | Status: {{ c.membership_status }} | Adherence: {{ c.adherence }}%</li>
      {% endfor %}
    </ul>
  </div>
  <div class="card">
    <h2>Logged Workouts ({{ workouts|length }})</h2>
    <ul>
      {% for w in workouts %}
        <li><strong>{{ w.client_name }}</strong>: {{ w.workout_type }} ({{ w.duration_min }} min) — {{ w.notes }}</li>
      {% endfor %}
    </ul>
  </div>
</body>
</html>
"""


def generate_program_for_client(client_name: str, goal: Optional[str] = None) -> dict:
    chosen_goal = goal if goal in PROGRAM_TEMPLATES else random.choice(list(PROGRAM_TEMPLATES.keys()))
    chosen_plan = random.choice(PROGRAM_TEMPLATES[chosen_goal])
    for client in clients_db:
        if client["name"].lower() == client_name.lower():
            client["program"] = chosen_plan
            return {"client_name": client["name"], "goal": chosen_goal, "program": chosen_plan}
    new_client = {
        "id": len(clients_db) + 1,
        "name": client_name,
        "age": 30,
        "weight": 75.0,
        "program": chosen_plan,
        "calories": 2200,
        "target_weight": 73.0,
        "membership_status": "Active",
        "adherence": 80,
    }
    clients_db.append(new_client)
    return {"client_name": client_name, "goal": chosen_goal, "program": chosen_plan}


@app.route("/")
def home():
    return render_template_string(
        HTML_TEMPLATE,
        version=APP_VERSION,
        clients=clients_db,
        workouts=workouts_db,
    )


@app.route("/health")
def health():
    return jsonify({"status": "UP", "service": "ACEest Fitness & Gym", "version": APP_VERSION}), 200


@app.route("/version")
def version():
    return jsonify({"app": "ACEest Fitness & Gym", "version": APP_VERSION}), 200


@app.route("/clients", methods=["GET", "POST"])
def clients():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "Client name is required"}), 400
        record = {
            "id": len(clients_db) + 1,
            "name": name,
            "age": int(data.get("age") or 30),
            "weight": float(data.get("weight") or 75.0),
            "program": data.get("program") or "Beginner",
            "calories": int(data.get("calories") or 2200),
            "target_weight": float(data.get("target_weight") or 72.0),
            "membership_status": data.get("membership_status") or "Active",
            "adherence": int(data.get("adherence") or 80),
        }
        clients_db.append(record)
        return jsonify(record), 201
    return jsonify({"clients": clients_db, "version": APP_VERSION}), 200


@app.route("/programs/generate", methods=["POST"])
def create_program():
    data = request.get_json(silent=True) or request.form
    client_name = (data.get("client_name") or "").strip()
    if not client_name:
        return jsonify({"error": "client_name is required"}), 400
    result = generate_program_for_client(client_name, data.get("goal"))
    return jsonify(result), 200


@app.route("/workouts", methods=["GET", "POST"])
def workouts():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        client_name = (data.get("client_name") or "").strip()
        workout_type = (data.get("workout_type") or "Strength").strip()
        duration_min = int(data.get("duration_min") or 45)
        if not client_name:
            return jsonify({"error": "client_name is required"}), 400
        entry = {
            "id": len(workouts_db) + 1,
            "client_name": client_name,
            "workout_type": workout_type,
            "duration_min": duration_min,
            "notes": data.get("notes") or "",
        }
        workouts_db.append(entry)
        return jsonify(entry), 201
    return jsonify({"workouts": workouts_db, "version": APP_VERSION}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
