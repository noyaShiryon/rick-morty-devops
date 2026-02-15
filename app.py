"""
app.py
------
Flask REST API that exposes Rick and Morty character data collected
by fetch_characters.py.

Endpoints:
    GET /             - Interactive HTML dashboard with character cards and modal popup.
    GET /healthcheck  - Returns service health status.
    GET /characters   - Returns all filtered characters as JSON.

Usage:
    python app.py

The application fetches and caches character data on startup to avoid
repeated API calls on every request.
"""

import json
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

@app.route("/", methods=["GET"])
def dashboard():
    """Render an HTML dashboard showing all filtered characters.

    Each card is clickable and opens a modal with full character details
    including gender, origin, location, episode count and status.

    Returns:
        HTML: A styled page with character cards and a detail modal.
    """
    cards_html = ""
    characters_json = json.dumps([
        {
            "id": c["id"],
            "name": c["name"],
            "status": c["status"],
            "species": c["species"],
            "gender": c["gender"],
            "origin": c["origin"]["name"],
            "location": c["location"]["name"],
            "image": c["image"],
            "episodes": len(c["episode"]),
            "url": c["url"],
        }
        for c in _characters
    ])

    for i, c in enumerate(_characters):
        name = c["name"]
        location = c["location"]["name"]
        image = c["image"]
        cards_html += f"""
        <div class="card" onclick="openModal({i})" role="button" tabindex="0"
             onkeydown="if(event.key==='Enter')openModal({i})">
            <img src="{image}" alt="{name}" loading="lazy">
            <div class="card-body">
                <div class="card-name">{name}</div>
                <div class="card-location">
                    <span class="location-icon">📍</span>{location}
                </div>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rick &amp; Morty – Earth Survivors</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #060a0f;
            --surface: #0d1520;
            --card: #111d2e;
            --border: #1a2d45;
            --green: #97ce4c;
            --cyan: #44d9e8;
            --text: #d4e8f0;
            --muted: #4a6880;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'DM Sans', sans-serif;
            min-height: 100vh;
        }}

        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(68,217,232,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(68,217,232,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }}

        header {{
            position: relative;
            z-index: 1;
            padding: 3rem 2rem 2rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
        }}

        header::after {{
            content: '';
            display: block;
            width: 120px;
            height: 3px;
            background: linear-gradient(90deg, var(--green), var(--cyan));
            margin: 1.5rem auto 0;
            border-radius: 2px;
        }}

        .header-eyebrow {{
            font-size: 0.7rem;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: var(--cyan);
            margin-bottom: 0.75rem;
        }}

        h1 {{
            font-family: 'Bebas Neue', sans-serif;
            font-size: clamp(2.5rem, 6vw, 5rem);
            letter-spacing: 3px;
            line-height: 1;
            background: linear-gradient(135deg, #fff 30%, var(--green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header-sub {{ margin-top: 0.75rem; color: var(--muted); font-size: 0.9rem; font-weight: 300; }}

        .stats-bar {{
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 1.25rem 2rem;
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            flex-wrap: wrap;
        }}

        .stat {{ display: flex; align-items: center; gap: 0.6rem; font-size: 0.85rem; }}

        .stat-dot {{
            width: 8px; height: 8px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}

        .stat-dot.green {{ background: var(--green); box-shadow: 0 0 8px var(--green); }}
        .stat-dot.cyan  {{ background: var(--cyan);  box-shadow: 0 0 8px var(--cyan); }}

        @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.4; }} }}

        .stat-value {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; color: var(--green); letter-spacing: 1px; }}
        .stat-label {{ color: var(--muted); }}

        .search-wrap {{
            position: relative; z-index: 1;
            padding: 1.5rem 2rem;
            max-width: 480px; margin: 0 auto;
        }}

        #search {{
            width: 100%;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem 1.25rem 0.75rem 2.75rem;
            color: var(--text);
            font-family: 'DM Sans', sans-serif;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }}

        #search:focus {{ border-color: var(--cyan); }}
        #search::placeholder {{ color: var(--muted); }}

        .search-icon {{
            position: absolute; left: 2.9rem; top: 50%;
            transform: translateY(-50%);
            color: var(--muted); font-size: 0.9rem; pointer-events: none;
        }}

        .grid {{
            position: relative; z-index: 1;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1.25rem;
            padding: 0 2rem 4rem;
            max-width: 1400px; margin: 0 auto;
        }}

        .card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
            animation: fadeIn 0.4s ease both;
        }}

        .card:hover {{
            transform: translateY(-4px);
            border-color: rgba(68,217,232,0.4);
            box-shadow: 0 8px 32px rgba(68,217,232,0.1);
        }}

        @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:translateY(0); }} }}

        .card img {{ width:100%; aspect-ratio:1; object-fit:cover; display:block; filter:saturate(0.9); transition:filter 0.2s; }}
        .card:hover img {{ filter:saturate(1.2); }}

        .card-body {{ padding: 0.85rem 1rem; }}
        .card-name {{ font-weight:500; font-size:0.9rem; margin-bottom:0.3rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
        .card-location {{ font-size:0.75rem; color:var(--muted); display:flex; align-items:center; gap:0.3rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
        .location-icon {{ font-size:0.7rem; flex-shrink:0; }}

        .no-results {{ display:none; grid-column:1/-1; text-align:center; padding:4rem; color:var(--muted); }}

        /* ------------------------------------------------------------------ */
        /* MODAL                                                               */
        /* ------------------------------------------------------------------ */
        .modal-overlay {{
            display: none;
            position: fixed; inset: 0; z-index: 100;
            background: rgba(0,0,0,0.75);
            backdrop-filter: blur(6px);
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }}

        .modal-overlay.open {{ display: flex; animation: overlayIn 0.2s ease; }}
        @keyframes overlayIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}

        .modal {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            max-width: 560px;
            width: 100%;
            overflow: hidden;
            animation: modalIn 0.25s cubic-bezier(0.34,1.56,0.64,1);
            position: relative;
        }}

        @keyframes modalIn {{ from {{ opacity:0; transform:scale(0.9) translateY(20px); }} to {{ opacity:1; transform:scale(1) translateY(0); }} }}

        .modal-top {{
            display: flex;
            gap: 1.5rem;
            padding: 1.75rem;
            border-bottom: 1px solid var(--border);
        }}

        .modal-img {{
            width: 120px; height: 120px;
            border-radius: 12px;
            object-fit: cover;
            flex-shrink: 0;
            border: 2px solid var(--border);
        }}

        .modal-title {{ flex: 1; }}

        .modal-name {{
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.8rem;
            letter-spacing: 1px;
            line-height: 1.1;
            margin-bottom: 0.6rem;
        }}

        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            background: rgba(151,206,76,0.15);
            border: 1px solid rgba(151,206,76,0.3);
            color: var(--green);
        }}

        .status-dot {{
            width: 6px; height: 6px;
            border-radius: 50%;
            background: var(--green);
            animation: pulse 2s infinite;
        }}

        .modal-body {{ padding: 1.5rem 1.75rem; }}

        .detail-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}

        .detail-item {{ display: flex; flex-direction: column; gap: 0.2rem; }}

        .detail-label {{
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--muted);
        }}

        .detail-value {{
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text);
        }}

        .detail-value.highlight {{ color: var(--cyan); }}

        .modal-footer {{
            padding: 1rem 1.75rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border);
        }}

        .modal-footer a {{
            font-size: 0.8rem;
            color: var(--cyan);
            text-decoration: none;
            opacity: 0.8;
            transition: opacity 0.2s;
        }}
        .modal-footer a:hover {{ opacity: 1; }}

        .btn-close {{
            background: var(--card);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.5rem 1.25rem;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.85rem;
            transition: border-color 0.2s;
        }}
        .btn-close:hover {{ border-color: var(--cyan); }}

        footer {{
            position: relative; z-index: 1;
            text-align: center;
            padding: 1.5rem;
            border-top: 1px solid var(--border);
            color: var(--muted);
            font-size: 0.75rem;
        }}
        footer a {{ color: var(--cyan); text-decoration: none; }}
    </style>
</head>
<body>
    <header>
        <div class="header-eyebrow">Rick &amp; Morty API · DevOps Exercise</div>
        <h1>Earth Survivors</h1>
        <p class="header-sub">Human · Alive · Earth Origin</p>
    </header>

    <div class="stats-bar">
        <div class="stat">
            <div class="stat-dot green"></div>
            <span class="stat-value">{len(_characters)}</span>
            <span class="stat-label">characters</span>
        </div>
        <div class="stat">
            <div class="stat-dot cyan"></div>
            <span class="stat-value">ALIVE</span>
            <span class="stat-label">status</span>
        </div>
        <div class="stat">
            <div class="stat-dot green"></div>
            <span class="stat-value">HUMAN</span>
            <span class="stat-label">species</span>
        </div>
        <div class="stat">
            <div class="stat-dot cyan"></div>
            <span class="stat-value">EARTH</span>
            <span class="stat-label">origin</span>
        </div>
    </div>

    <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input id="search" type="text" placeholder="Search characters..." oninput="filterCards(this.value)">
    </div>

    <div class="grid" id="grid">
        {cards_html}
        <div class="no-results" id="no-results">No characters found.</div>
    </div>

    <!-- Modal -->
    <div class="modal-overlay" id="modal-overlay" onclick="closeOnOverlay(event)">
        <div class="modal" id="modal">
            <div class="modal-top">
                <img id="m-img" class="modal-img" src="" alt="">
                <div class="modal-title">
                    <div id="m-name" class="modal-name"></div>
                    <div class="status-badge">
                        <div class="status-dot"></div>
                        <span>Alive</span>
                    </div>
                </div>
            </div>
            <div class="modal-body">
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Species</span>
                        <span id="m-species" class="detail-value"></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Gender</span>
                        <span id="m-gender" class="detail-value"></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Origin</span>
                        <span id="m-origin" class="detail-value highlight"></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Current Location</span>
                        <span id="m-location" class="detail-value"></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Episodes</span>
                        <span id="m-episodes" class="detail-value highlight"></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Character ID</span>
                        <span id="m-id" class="detail-value"></span>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <a id="m-url" href="#" target="_blank">View on API ↗</a>
                <button class="btn-close" onclick="closeModal()">Close</button>
            </div>
        </div>
    </div>

    <footer>
        Data from <a href="https://rickandmortyapi.com" target="_blank">rickandmortyapi.com</a>
        &nbsp;·&nbsp; REST API at
        <a href="/characters">/characters</a> &nbsp;·&nbsp;
        <a href="/healthcheck">/healthcheck</a>
    </footer>

    <script>
        const characters = {characters_json};

        // Stagger card animations
        document.querySelectorAll('.card').forEach((card, i) => {{
            card.style.animationDelay = (i * 20) + 'ms';
        }});

        // Search filter
        function filterCards(query) {{
            const q = query.toLowerCase();
            const cards = document.querySelectorAll('.card');
            let visible = 0;
            cards.forEach(card => {{
                const name = card.querySelector('.card-name').textContent.toLowerCase();
                const location = card.querySelector('.card-location').textContent.toLowerCase();
                const match = name.includes(q) || location.includes(q);
                card.style.display = match ? '' : 'none';
                if (match) visible++;
            }});
            document.getElementById('no-results').style.display = visible === 0 ? 'block' : 'none';
        }}

        // Modal
        function openModal(index) {{
            const c = characters[index];
            document.getElementById('m-img').src = c.image;
            document.getElementById('m-img').alt = c.name;
            document.getElementById('m-name').textContent = c.name;
            document.getElementById('m-species').textContent = c.species;
            document.getElementById('m-gender').textContent = c.gender;
            document.getElementById('m-origin').textContent = c.origin;
            document.getElementById('m-location').textContent = c.location;
            document.getElementById('m-episodes').textContent = c.episodes + ' episodes';
            document.getElementById('m-id').textContent = '#' + c.id;
            document.getElementById('m-url').href = c.url;
            document.getElementById('modal-overlay').classList.add('open');
            document.body.style.overflow = 'hidden';
        }}

        function closeModal() {{
            document.getElementById('modal-overlay').classList.remove('open');
            document.body.style.overflow = '';
        }}

        function closeOnOverlay(e) {{
            if (e.target === document.getElementById('modal-overlay')) closeModal();
        }}

        // Close on Escape key
        document.addEventListener('keydown', e => {{
            if (e.key === 'Escape') closeModal();
        }});
    </script>
</body>
</html>"""
    return html, 200


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