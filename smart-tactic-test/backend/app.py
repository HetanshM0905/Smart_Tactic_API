from flask import Flask, jsonify, make_response
from flask_cors import CORS
from tinydb import TinyDB
import os
from typing import List

app = Flask(__name__)

# --- CORS: allow Angular dev server ---
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Origin"] = "http://localhost:4200"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


# ---------- path resolution ----------
def _candidate_paths() -> List[str]:
    env = os.environ.get("SMART_TACTICS_DB")
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    cwd = os.getcwd()

    cand = []
    if env:
        cand.append(os.path.abspath(env))
    cand.extend([
        os.path.join(here, "data", "form_db.json"),
        os.path.join(here, "form_db.json"),
        os.path.join(root, "data", "form_db.json"),
        os.path.join(root, "form_db.json"),
        os.path.join(cwd, "data", "form_db.json"),
        os.path.join(cwd, "form_db.json"),
    ])
    # De-dup while preserving order
    seen = set()
    ordered = []
    for p in cand:
        if p not in seen:
            seen.add(p)
            ordered.append(p)
    return ordered

def _resolve_db_path() -> str:
    candidates = _candidate_paths()
    print("\n[Flask] CWD        :", os.getcwd())
    print("[Flask] __file__   :", os.path.abspath(__file__))
    print("[Flask] Candidates :")
    for p in candidates:
        print("   -", p, " [EXISTS]" if os.path.exists(p) else "")
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""


# ---------- helpers ----------
def read_table(db: TinyDB, table_name: str):
    """
    Return the table in a way that matches common TinyDB usage:
      - If first doc has 'data', return that inner dict (common pattern).
      - Else if single doc, return it.
      - Else return list of docs.
    """
    table = db.table(table_name)
    docs = table.all()
    if not docs:
        return []
    first = docs[0]
    if isinstance(first, dict) and "data" in first:
        return first["data"]
    if len(docs) == 1:
        return first
    return docs


# ---------- routes ----------
@app.route("/", methods=["GET"])
def index():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static":  # exclude Flask static files
            routes.append({
                "path": str(rule),
                "methods": sorted(list(rule.methods - {"HEAD", "OPTIONS"}))
            })
    # sort alphabetically by path
    routes = sorted(routes, key=lambda r: r["path"])
    return jsonify({
        "service": "Smart Tactics API",
        "status": "ok",
        "endpoints": routes
    }), 200


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200


@app.route("/api/form-config", methods=["GET"])
def get_form_config():
    db_path = _resolve_db_path()
    if not db_path:
        return make_response(
            jsonify({
                "error": "TinyDB file form_db.json not found in expected locations.",
                "hint": "Set SMART_TACTICS_DB=/absolute/path/to/form_db.json or move your DB to backend/data/form_db.json",
            }),
            500,
        )

    print(f"[Flask] Using TinyDB at: {db_path}\n")
    db = TinyDB(db_path)

    form_structure = read_table(db, "form_structure")
    form_options   = read_table(db, "form_options")

    resp = make_response(jsonify({"structure": form_structure, "options": form_options}), 200)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.route("/api/form-structure", methods=["GET"])
def get_form_structure():
    db_path = _resolve_db_path()
    if not db_path:
        return make_response(jsonify({"error": "Database not found"}), 500)
    
    db = TinyDB(db_path)
    form_structure = read_table(db, "form_structure")
    return jsonify(form_structure)


@app.route("/api/form-options", methods=["GET"])
def get_form_options():
    db_path = _resolve_db_path()
    if not db_path:
        return make_response(jsonify({"error": "Database not found"}), 500)
    
    db = TinyDB(db_path)
    form_options = read_table(db, "form_options")
    return jsonify(form_options)


if __name__ == "__main__":
    app.run(debug=True, port=5000)