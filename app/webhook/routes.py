from datetime import datetime
from aiohttp import Payload
from flask import Blueprint, json, jsonify, render_template, request
from app.extensions import mongo


webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/')
def home():
    return render_template("index.html")

@webhook.route('/receiver', methods=["POST"])
def receiver():

    event_type = request.headers.get("X-GitHub-Event")
    payload = request.json
    event = {}

    if event_type=="push":
        event = {
            "request_id": payload["after"],
            "author": payload["pusher"]["name"],
            "action": "PUSH",
            "from_branch": None,
            "to_branch": payload["ref"].split("/")[-1],
            "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        }

    elif event_type == "pull_request":
        pr = payload["pull_request"]
        event = {
            "request_id": str(pr["id"]),
            "author": pr["user"]["login"],
            "action": "PULL_REQUEST" if not pr["merged"] else "MERGE",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        }
    
    if event:
        mongo.db.events.insert_one(event)
        return jsonify({"msg": "event stored"}), 200
    return jsonify({"msg": "ignored"}), 400


@webhook.route('/events', methods=["GET"])
def get_events():
    events = list(mongo.db.events.find().sort("timestamp", -1))
    for e in events:
        e["_id"] = str(e["_id"])
    return jsonify(events)
