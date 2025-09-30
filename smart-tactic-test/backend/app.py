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
        os.path.join(root, "chat_service", "smart_tactic_tinydb.json") ])
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
def read_workflow_data(db_path: str, workflow_id: str = "2"):
    """
    Read workflow data from smart_tactic_tinydb.json structure.
    Since the file is a plain JSON object (not TinyDB format), we read it directly.
    Returns the workflow data for the specified workflow ID.
    """
    import json
    try:
        with open(db_path, 'r') as f:
            raw_data = json.load(f)
        
        if isinstance(raw_data, dict) and "workflows" in raw_data:
            workflows = raw_data["workflows"]
            return workflows.get(workflow_id, {})
        
        return None
    except Exception as e:
        print(f"Error reading workflow data: {e}")
        return None

def read_form_structure(db_path: str, workflow_id: str = "2"):
    """Extract form_structure from the workflow"""
    workflow = read_workflow_data(db_path, workflow_id)
    if not workflow:
        return {}
    
    form_structure = workflow.get("form_structure", {})
    # Return the nested structure under "1" -> "data" if it exists
    if "1" in form_structure and "data" in form_structure["1"]:
        return form_structure["1"]["data"]
    return form_structure

def read_form_options(db_path: str, workflow_id: str = "2"):
    """Extract form_options from the workflow"""
    workflow = read_workflow_data(db_path, workflow_id)
    if not workflow:
        return {}
    
    form_options = workflow.get("form_options", {})
    # Return the nested structure under "1" -> "data" if it exists
    if "1" in form_options and "data" in form_options["1"]:
        return form_options["1"]["data"]
    return form_options


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
                "error": "TinyDB file smart_tactic_tinydb.json not found in expected locations.",
                "hint": "Set SMART_TACTICS_DB=/absolute/path/to/smart_tactic_tinydb.json or move your DB to backend/data/smart_tactic_tinydb.json",
            }),
            500,
        )

    print(f"[Flask] Using database at: {db_path}\n")

    form_structure = read_form_structure(db_path)
    form_options = read_form_options(db_path)

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
    
    form_structure = read_form_structure(db_path)
    return jsonify(form_structure)


@app.route("/api/form-options", methods=["GET"])
def get_form_options():
    db_path = _resolve_db_path()
    if not db_path:
        return make_response(jsonify({"error": "Database not found"}), 500)
    
    form_options = read_form_options(db_path)
    return jsonify(form_options)


if __name__ == "__main__":
    app.run(debug=True, port=5000)