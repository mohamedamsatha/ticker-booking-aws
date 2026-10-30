
from flask import Flask, render_template, jsonify, request
import boto3
import json
from uuid import uuid4

app = Flask(__name__)

# --------------------------------
# AWS SQS Configuration
# --------------------------------

sqs = boto3.client(
    "sqs",
    region_name="eu-north-1"
)

QUEUE_URL = "https://sqs.eu-north-1.amazonaws.com/560245954931/ticket"


# --------------------------------
# Events Data
# --------------------------------

EVENTS = [
    {
        "id": 1,
        "name": "Live Music Festival",
        "category": "Music",
        "date": "2026-11-21",
        "time": "6:30 PM",
        "venue": "Chennai Trade Centre",
        "price": 799,
        "available": 120
    },
    {
        "id": 2,
        "name": "Future Tech Summit",
        "category": "Technology",
        "date": "2026-11-28",
        "time": "9:00 AM",
        "venue": "ITC Grand Chola, Chennai",
        "price": 1299,
        "available": 80
    },
    {
        "id": 3,
        "name": "Indie Nights",
        "category": "Music",
        "date": "2026-12-05",
        "time": "7:00 PM",
        "venue": "Phoenix Marketcity, Chennai",
        "price": 599,
        "available": 65
    },
    {
        "id": 4,
        "name": "Creative Minds Workshop",
        "category": "Workshop",
        "date": "2026-12-12",
        "time": "10:00 AM",
        "venue": "Anna Centenary Library, Chennai",
        "price": 399,
        "available": 45
    }
]


# --------------------------------
# Home Page
# --------------------------------

@app.route("/")
def home():
    return render_template("index.html", events=EVENTS)


# --------------------------------
# Get All Events API
# --------------------------------

@app.route("/api/events")
def get_events():
    return jsonify({
        "events": EVENTS
    })


# --------------------------------
# Health Check API
# --------------------------------

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    }), 200


# --------------------------------
# SQS Booking API
# --------------------------------

@app.route("/api/book", methods=["POST"])
def book_ticket():

    data = request.get_json(silent=True) or {}

    event_id = data.get("event_id")
    customer_name = str(data.get("customer_name") or "").strip()
    customer_email = str(data.get("customer_email") or "").strip()
    quantity = data.get("quantity")

    # Validate required fields
    if (
        event_id is None
        or not customer_name
        or not customer_email
        or quantity is None
    ):
        return jsonify({
            "error": "All booking fields are required"
        }), 400

    # Validate event ID
    try:
        event_id = int(event_id)
    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid event ID"
        }), 400

    # Validate quantity
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({
            "error": "Quantity must be a number"
        }), 400

    if quantity < 1 or quantity > 6:
        return jsonify({
            "error": "Quantity must be between 1 and 6"
        }), 400

    # Basic email validation
    if (
        "@" not in customer_email
        or "." not in customer_email.split("@")[-1]
    ):
        return jsonify({
            "error": "Invalid email address"
        }), 400

    # Find selected event
    event = next(
        (e for e in EVENTS if e["id"] == event_id),
        None
    )

    if event is None:
        return jsonify({
            "error": "Event not found"
        }), 404

    # Check available tickets
    if quantity > event["available"]:
        return jsonify({
            "error": "Not enough tickets available"
        }), 400

    # Prepare booking message
    booking = {
        "booking_id": str(uuid4()),
        "event_id": event["id"],
        "event_name": event["name"],
        "customer_name": customer_name,
        "customer_email": customer_email,
        "quantity": quantity,
        "unit_price": event["price"],
        "total_amount": event["price"] * quantity
    }

    # Send message to AWS SQS
    try:
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(booking)
        )

    except Exception:
        app.logger.exception("Failed to send booking to SQS")

        return jsonify({
            "error": "Unable to process booking request. Please try again."
        }), 503

    return jsonify({
        "message": "Booking request sent to SQS successfully",
        "booking_id": booking["booking_id"],
        "sqs_message_id": response["MessageId"]
    }), 202


# --------------------------------
# Run Flask Application
# --------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

