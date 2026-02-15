"""
app.py
------
Flask REST API that exposes Rick and Morty character data collected
by fetch_characters.py.

Endpoints:
    GET /healthcheck  - Returns service health status.
    GET /characters   - Returns all filtered characters as JSON.

Usage:
    python app.py

The application fetches and caches character data on startup to avoid
repeated API calls on every request.
"""

from flask import Flask, jsonify
from fetch_characters import fetch_all_characters, filter_characters

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = Flask(__name__)

# Fetch and cache data once at startup
print("Loading character data...")
_characters = filter_characters(fetch_all_characters())
print(f"Cached {len(_characters)} characters.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    """Return service health status.

    Returns:
        JSON: ``{"status": "ok"}`` with HTTP 200.
    """
    return jsonify({"status": "ok"}), 200


@app.route("/characters", methods=["GET"])
def get_characters():
    """Return all filtered Rick and Morty characters as JSON.

    Characters are pre-filtered to:
        - Species  : Human
        - Status   : Alive
        - Origin   : Contains "Earth"

    Returns:
        JSON: Object containing a ``count`` field and a ``characters``
        array, each item with ``name``, ``location``, and ``image`` fields.
    """
    result = [
        {
            "name": c["name"],
            "location": c["location"]["name"],
            "image": c["image"],
        }
        for c in _characters
    ]
    return jsonify({"count": len(result), "characters": result}), 200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)