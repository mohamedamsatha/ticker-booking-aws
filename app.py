
from flask import Flask, render_template, jsonify

app = Flask(__name__)

EVENTS = [
    {
        "id": 1,
        "name": "Live Music Festival",
        "category": "Music",
        "date": "2026-11-21",
        "time": "6:30 PM",
        "venue": "Chennai Trade Centre",
        "price": 799,
        "available": 120,
        "image": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?auto=format&fit=crop&w=1000&q=85",
        "tag": "POPULAR"
    },
    {
        "id": 2,
        "name": "Future Tech Summit",
        "category": "Technology",
        "date": "2026-11-28",
        "time": "9:00 AM",
        "venue": "ITC Grand Chola, Chennai",
        "price": 1299,
        "available": 80,
        "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1000&q=85",
        "tag": "TRENDING"
    },
    {
        "id": 3,
        "name": "Indie Nights",
        "category": "Music",
        "date": "2026-12-05",
        "time": "7:00 PM",
        "venue": "Phoenix Marketcity, Chennai",
        "price": 599,
        "available": 65,
        "image": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1000&q=85",
        "tag": "LIMITED"
    },
    {
        "id": 4,
        "name": "Creative Minds Workshop",
        "category": "Workshop",
        "date": "2026-12-12",
        "time": "10:00 AM",
        "venue": "Anna Centenary Library, Chennai",
        "price": 399,
        "available": 45,
        "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1000&q=85",
        "tag": "NEW"
    },
]

@app.route("/")
def home():
    return render_template("index.html", events=EVENTS)

@app.route("/api/events")
def get_events():
    return jsonify({"events": EVENTS})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(debug=True)
