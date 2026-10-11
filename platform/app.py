#!/usr/bin/env python3
"""
Operation E Corp Breach - CTF platform backend

Server-side flag validation and sequential unlocking for EC-01 to EC-03.

Design points that matter for the report:
  * Correct flags NEVER reach the browser. They are stored as SHA-256 hashes
    in secrets/flags.json and compared on the server.
  * Challenge artefacts are NOT in the web root. They are served by
    /api/download/<stage>, which refuses unless the player has unlocked
    that stage. Guessing a URL gets you nothing.
  * Unlock state lives in the database, not in the session cookie or in
    localStorage, so a player cannot edit their way forward.

Run:
    pip install -r requirements.txt
    python3 app.py
    -> http://127.0.0.1:5000
"""

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from functools import wraps

from flask import (Flask, g, jsonify, request, send_file, send_from_directory,
                   session)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_DIR = os.path.join(BASE_DIR, "secrets")      # never served
ARTEFACT_DIR = os.path.join(BASE_DIR, "artefacts")   # never served directly
DB_PATH = os.path.join(BASE_DIR, "ctf.db")
FLAGS_PATH = os.path.join(SECRETS_DIR, "flags.json")

app = Flask(__name__, static_folder=None)

# A fresh secret key on every start would log everyone out on restart, so it
# is persisted to secrets/. It is generated on first run.
_KEYFILE = os.path.join(SECRETS_DIR, "session.key")
os.makedirs(SECRETS_DIR, exist_ok=True)
if not os.path.exists(_KEYFILE):
    with open(_KEYFILE, "w") as f:
        f.write(secrets.token_hex(32))
    os.chmod(_KEYFILE, 0o600)
with open(_KEYFILE) as f:
    app.secret_key = f.read().strip()

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # JavaScript cannot read the session cookie
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 12,
)


# --------------------------------------------------------------- challenges --
# Public metadata only. Nothing here is secret - it is safe to send to the
# browser. The flags live in secrets/flags.json and never appear in a response.
CHALLENGES = [
    {
        "id": "ec01",
        "number": "01",
        "name": "The Forged Security Alert",
        "category": "DIGITAL FORENSICS",
        "difficulty": "EASY",
        "points": 100,
        "artefact": "suspicious_email.eml",
        "requires": None,
        "hints": [
            {"cost": 0,  "text": "An .eml file is plain text. Open it in a text editor, not a mail client."},
            {"cost": 10, "text": "If you replied to this message, where would the reply actually go?"},
            {"cost": 25, "text": "Headers beginning with X- are non-standard. Read all of them."},
        ],
    },
    {
        "id": "ec02",
        "number": "02",
        "name": "The Password-Protected Image",
        "category": "STEGANOGRAPHY",
        "difficulty": "EASY",
        "points": 100,
        "artefact": "company_event.jpg",
        "requires": "ec01",
        "hints": [
            {"cost": 0,  "text": "Before looking at the pixels, look at the file's metadata. exiftool reads it."},
            {"cost": 10, "text": "The Comment field is an instruction, not the password. Apply it to what EC-01 gave you."},
            {"cost": 25, "text": "The tool is steghide: steghide extract -sf <image> -p <password>"},
        ],
    },
    {
        "id": "ec03",
        "number": "03",
        "name": "The Three-Layer Attacker Message",
        "category": "CRYPTOGRAPHY",
        "difficulty": "MODERATE",
        "points": 150,
        "artefact": "attacker_message.txt",
        "requires": "ec02",
        "hints": [
            {"cost": 0,  "text": "Trailing = and an A-Z a-z 0-9 + / alphabet. Start there."},
            {"cost": 15, "text": "Under the first layer is an even-length string of 0-9a-f only."},
            {"cost": 30, "text": "The final layer is a Vigenere cipher. The key is the one word from EC-02."},
        ],
    },
    {
        "id": "ec04",
        "number": "04",
        "name": "The Compromised Employee Portal",
        "category": "WEB SECURITY",
        "difficulty": "MODERATE",
        "points": 150,
        # Interactive stage: the "evidence" download is an access card that
        # tells the player where the live portal is. The portal itself runs
        # in its own Docker container (stage04_web) on 127.0.0.1:8080.
        "artefact": "ec04_portal_access.txt",
        "requires": "ec03",
        "hints": [
            {"cost": 0,  "text": "The portal is an ordinary website. View its page source and check what crawlers are told to ignore (robots.txt)."},
            {"cost": 10, "text": "robots.txt points at a backup file. Old backups often leak internal API paths."},
            {"cost": 25, "text": "The employee API has no access control. Look up employee 1042's open incident, then read that incident."},
        ],
    },
    {
        "id": "ec05",
        "number": "05",
        "name": "Tracing the Data Exfiltration",
        "category": "NETWORKING",
        "difficulty": "MOD-HARD",
        "points": 200,
        "artefact": "network_capture.pcap",
        "requires": "ec04",
        "hints": [
            {"cost": 0,  "text": "Open the capture in Wireshark and filter for http."},
            {"cost": 15, "text": "One POST request looks different from the normal browsing. Right-click it and Follow the HTTP/TCP stream."},
            {"cost": 30, "text": "That stream carries the flag plus the Stage 6 Linux host and the analyst login, in plain text."},
        ],
    },
    {
        "id": "ec06",
        "number": "06",
        "name": "The Final Breach Investigation",
        "category": "LINUX - SYSTEM SECURITY",
        "difficulty": "HARD",
        "points": 300,
        # Interactive stage: the "evidence" download is an access card with
        # the SSH details. The box runs in its own container (stage06_linux)
        # on 127.0.0.1:2222.
        "artefact": "ec06_ssh_access.txt",
        "requires": "ec05",
        "hints": [
            {"cost": 0,  "text": "SSH in with the analyst login from Stage 5. Hidden files start with a dot - use ls -a."},
            {"cost": 20, "text": "Search the system log for the incident reference ECORP-774. It names a protected archive."},
            {"cost": 40, "text": "The archive password joins two earlier clues: the EC-03 key and the ECORP-104 number -> NIGHTSHIFT104."},
        ],
    },
]
CHALLENGE_BY_ID = {c["id"]: c for c in CHALLENGES}


def load_flags():
    """Read the SHA-256 flag hashes. Called per request so flags.json can be
    edited without restarting the server."""
    if not os.path.isfile(FLAGS_PATH):
        raise RuntimeError(f"missing {FLAGS_PATH} - run seed_flags.py first")
    with open(FLAGS_PATH) as f:
        return json.load(f)


def flag_hash(value):
    """Normalise then hash. Trailing whitespace from a copy-paste is the most
    common reason a correct flag gets rejected, so it is stripped here."""
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- database --
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            pw_hash  TEXT NOT NULL,
            salt     TEXT NOT NULL,
            created  INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS solves (
            user_id      INTEGER NOT NULL,
            challenge_id TEXT NOT NULL,
            points       INTEGER NOT NULL,
            solved_at    INTEGER NOT NULL,
            PRIMARY KEY (user_id, challenge_id)
        );
        CREATE TABLE IF NOT EXISTS hints_taken (
            user_id      INTEGER NOT NULL,
            challenge_id TEXT NOT NULL,
            hint_index   INTEGER NOT NULL,
            cost         INTEGER NOT NULL,
            PRIMARY KEY (user_id, challenge_id, hint_index)
        );
        CREATE TABLE IF NOT EXISTS attempts (
            user_id      INTEGER NOT NULL,
            challenge_id TEXT NOT NULL,
            correct      INTEGER NOT NULL,
            at           INTEGER NOT NULL
        );
    """)
    conn.commit()
    conn.close()


# ------------------------------------------------------------------- auth --
def hash_password(password, salt=None):
    """PBKDF2-HMAC-SHA256. Plain passwords are never stored."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return digest.hex(), salt


def current_user():
    uid = session.get("uid")
    if uid is None:
        return None
    return db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if current_user() is None:
            return jsonify(error="Not signed in."), 401
        return fn(*a, **kw)
    return wrapper


# ------------------------------------------------------------ player state --
def solved_ids(uid):
    rows = db().execute("SELECT challenge_id FROM solves WHERE user_id = ?", (uid,))
    return {r["challenge_id"] for r in rows}


def is_unlocked(challenge, solved):
    """A challenge is available when its prerequisite has been solved.
    This is the dependency chain, enforced server-side."""
    return challenge["requires"] is None or challenge["requires"] in solved


def build_state(user):
    uid = user["id"]
    solved = solved_ids(uid)

    hint_rows = db().execute(
        "SELECT challenge_id, hint_index, cost FROM hints_taken WHERE user_id = ?", (uid,)
    ).fetchall()
    taken = {}
    penalty = 0
    for r in hint_rows:
        taken.setdefault(r["challenge_id"], []).append(r["hint_index"])
        penalty += r["cost"]

    earned = db().execute(
        "SELECT COALESCE(SUM(points), 0) AS p FROM solves WHERE user_id = ?", (uid,)
    ).fetchone()["p"]

    out = []
    for c in CHALLENGES:
        unlocked = is_unlocked(c, solved)
        taken_idx = sorted(taken.get(c["id"], []))
        out.append({
            "id": c["id"],
            "number": c["number"],
            "name": c["name"],
            "category": c["category"],
            "difficulty": c["difficulty"],
            "points": c["points"],
            "artefact": c["artefact"] if unlocked else None,
            "requires": c["requires"],
            "unlocked": unlocked,
            "solved": c["id"] in solved,
            # Only the text of hints already paid for is sent. The rest stay
            # on the server so they cannot be read out of the page source.
            "hints": [
                {
                    "index": i,
                    "cost": h["cost"],
                    "taken": i in taken_idx,
                    "text": h["text"] if i in taken_idx else None,
                }
                for i, h in enumerate(c["hints"])
            ],
        })

    return {
        "user": user["username"],
        "score": max(0, earned - penalty),
        "earned": earned,
        "penalty": penalty,
        "total": sum(c["points"] for c in CHALLENGES),
        "challenges": out,
    }


# ------------------------------------------------------------------ routes --
@app.post("/api/register")
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not (3 <= len(username) <= 18) or not username.replace("_", "").isalnum():
        return jsonify(error="Callsign must be 3-18 characters, letters, digits or underscore."), 400
    if len(password) < 6:
        return jsonify(error="Password must be at least 6 characters."), 400

    pw_hash, salt = hash_password(password)
    try:
        cur = db().execute(
            "INSERT INTO users (username, pw_hash, salt, created) VALUES (?,?,?,?)",
            (username, pw_hash, salt, int(time.time())),
        )
        db().commit()
    except sqlite3.IntegrityError:
        return jsonify(error="That callsign is already taken."), 409

    session.clear()
    session["uid"] = cur.lastrowid
    session.permanent = True
    return jsonify(ok=True, state=build_state(current_user()))


@app.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    row = db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    # Same message either way so the response cannot be used to discover
    # which callsigns exist.
    if row is None:
        return jsonify(error="Invalid callsign or password."), 401
    attempt, _ = hash_password(password, row["salt"])
    if not hmac.compare_digest(attempt, row["pw_hash"]):
        return jsonify(error="Invalid callsign or password."), 401

    session.clear()
    session["uid"] = row["id"]
    session.permanent = True
    return jsonify(ok=True, state=build_state(row))


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify(ok=True)


@app.get("/api/state")
def api_state():
    user = current_user()
    if user is None:
        # Anonymous view: names and points only, nothing playable.
        return jsonify(
            user=None,
            challenges=[{
                "id": c["id"], "number": c["number"], "name": c["name"],
                "category": c["category"], "difficulty": c["difficulty"],
                "points": c["points"], "requires": c["requires"],
                "unlocked": False, "solved": False, "artefact": None,
                "hints": [{"index": i, "cost": h["cost"], "taken": False, "text": None}
                          for i, h in enumerate(c["hints"])],
            } for c in CHALLENGES],
            total=sum(c["points"] for c in CHALLENGES),
        )
    return jsonify(build_state(user))


@app.post("/api/submit")
@login_required
def api_submit():
    """Server-side flag validation. The correct value is never sent back,
    not even on a wrong answer - the response is only true or false."""
    user = current_user()
    data = request.get_json(silent=True) or {}
    cid = data.get("challenge")
    submitted = data.get("flag") or ""

    challenge = CHALLENGE_BY_ID.get(cid)
    if challenge is None:
        return jsonify(error="Unknown challenge."), 404

    solved = solved_ids(user["id"])
    if not is_unlocked(challenge, solved):
        return jsonify(error="That challenge is still locked."), 403
    if cid in solved:
        return jsonify(ok=True, correct=True, already=True, state=build_state(user))

    # Simple brute-force brake: 12 wrong answers per challenge per minute.
    window = int(time.time()) - 60
    recent = db().execute(
        "SELECT COUNT(*) AS n FROM attempts WHERE user_id=? AND challenge_id=? "
        "AND correct=0 AND at > ?", (user["id"], cid, window)
    ).fetchone()["n"]
    if recent >= 12:
        return jsonify(error="Too many attempts. Wait a minute and try again."), 429

    correct = hmac.compare_digest(flag_hash(submitted), load_flags().get(cid, ""))
    db().execute(
        "INSERT INTO attempts (user_id, challenge_id, correct, at) VALUES (?,?,?,?)",
        (user["id"], cid, 1 if correct else 0, int(time.time())),
    )

    if correct:
        db().execute(
            "INSERT OR IGNORE INTO solves (user_id, challenge_id, points, solved_at) "
            "VALUES (?,?,?,?)",
            (user["id"], cid, challenge["points"], int(time.time())),
        )
    db().commit()

    return jsonify(ok=True, correct=correct, state=build_state(current_user()))


@app.post("/api/hint")
@login_required
def api_hint():
    """Reveal one hint and record its penalty. Untaken hint text stays server
    side, so it cannot be read out of the page source."""
    user = current_user()
    data = request.get_json(silent=True) or {}
    cid = data.get("challenge")
    idx = data.get("index")

    challenge = CHALLENGE_BY_ID.get(cid)
    if challenge is None or not isinstance(idx, int) or not (0 <= idx < len(challenge["hints"])):
        return jsonify(error="Unknown hint."), 404
    if not is_unlocked(challenge, solved_ids(user["id"])):
        return jsonify(error="That challenge is still locked."), 403

    hint = challenge["hints"][idx]
    db().execute(
        "INSERT OR IGNORE INTO hints_taken (user_id, challenge_id, hint_index, cost) "
        "VALUES (?,?,?,?)", (user["id"], cid, idx, hint["cost"])
    )
    db().commit()
    return jsonify(ok=True, text=hint["text"], state=build_state(current_user()))


@app.get("/api/download/<cid>")
@login_required
def api_download(cid):
    """Artefacts live outside the web root. This is the only way to reach one,
    and it refuses unless the player has unlocked that stage."""
    user = current_user()
    challenge = CHALLENGE_BY_ID.get(cid)
    if challenge is None:
        return jsonify(error="Unknown challenge."), 404
    if not is_unlocked(challenge, solved_ids(user["id"])):
        return jsonify(error="That challenge is still locked."), 403

    path = os.path.join(ARTEFACT_DIR, challenge["artefact"])
    if not os.path.isfile(path):
        return jsonify(error=f"Artefact missing on the server: {challenge['artefact']}"), 500
    return send_file(path, as_attachment=True, download_name=challenge["artefact"])


@app.get("/api/scoreboard")
def api_scoreboard():
    rows = db().execute("""
        SELECT u.username,
               COALESCE(SUM(s.points), 0) -
               COALESCE((SELECT SUM(cost) FROM hints_taken h WHERE h.user_id = u.id), 0)
               AS score,
               COUNT(s.challenge_id) AS solves,
               COALESCE(MAX(s.solved_at), 0) AS last_solve
        FROM users u
        LEFT JOIN solves s ON s.user_id = u.id
        GROUP BY u.id
        HAVING solves > 0
        ORDER BY score DESC, last_solve ASC
        LIMIT 25
    """).fetchall()
    return jsonify(rows=[dict(r) for r in rows])


# ------------------------------------------------------------ static files --
@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename):
    """Serve only the page itself. secrets/, artefacts/ and the database are
    outside what this will hand out."""
    blocked = ("secrets", "artefacts", "app.py", "ctf.db", "seed_flags.py")
    if filename.split("/")[0] in blocked or filename.endswith(".py"):
        return jsonify(error="Not found."), 404
    full = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(full):
        return jsonify(error="Not found."), 404
    return send_from_directory(BASE_DIR, filename)


if __name__ == "__main__":
    init_db()

    missing = [c["artefact"] for c in CHALLENGES
               if not os.path.isfile(os.path.join(ARTEFACT_DIR, c["artefact"]))]
    if missing:
        print("[WARN] artefacts missing from artefacts/ :", ", ".join(missing))
        print("       Copy them from your ecorp-ctf public/ folders.")
    if not os.path.isfile(FLAGS_PATH):
        print("[WARN] secrets/flags.json not found - run: python3 seed_flags.py")

    print()
    print("  Operation E Corp Breach - platform running")
    print("  http://127.0.0.1:5000")
    print()
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=5000, debug=False)
