"""
SkillPilot AI — Flask backend.

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""
import os
import io

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename

from database import db
from agents.planner_agent import PlannerAgent

# Optional resume file parsing (pdf / docx). Falls back to plain text if
# these libs aren't installed.
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    import docx as docx_lib
except Exception:
    docx_lib = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "skillpilot-dev-secret-change-me")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB

planner = PlannerAgent()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(filepath, ext):
    if ext == "txt":
        with open(filepath, "r", errors="ignore") as f:
            return f.read()
    if ext == "pdf":
        if PdfReader is None:
            return ""
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext == "docx":
        if docx_lib is None:
            return ""
        d = docx_lib.Document(filepath)
        return "\n".join(p.text for p in d.paragraphs)
    return ""


# ---------------------------------------------------------------- pages ----
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ------------------------------------------------------------- API: auth ---
@app.route("/api/onboard", methods=["POST"])
def api_onboard():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    target_role = (data.get("target_role") or "").strip()

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    student = db.get_or_create_student(name, email, target_role or None)
    session["student_id"] = student["id"]
    return jsonify({"student": student, "system": planner.system_status()})


@app.route("/api/me")
def api_me():
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"student": None})
    return jsonify({"student": db.get_student(student_id)})


# ------------------------------------------------------- API: resume upload
@app.route("/api/upload_resume", methods=["POST"])
def api_upload_resume():
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"error": "no active session — please onboard first"}), 401

    if "resume" not in request.files:
        return jsonify({"error": "no file uploaded"}), 400
    file = request.files["resume"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "please upload a .pdf, .docx, or .txt file"}), 400

    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, f"{student_id}_{filename}")
    file.save(filepath)

    ext = filename.rsplit(".", 1)[1].lower()
    raw_text = extract_text_from_file(filepath, ext)

    if not raw_text.strip():
        return jsonify({"error": "couldn't extract any text from that file — try a .txt or a text-based PDF"}), 422

    analysis = planner.process_resume(student_id, filename, raw_text)
    return jsonify({"analysis": analysis})


# ---------------------------------------------------- API: full pipeline ---
@app.route("/api/generate_plan", methods=["POST"])
def api_generate_plan():
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"error": "no active session — please onboard first"}), 401

    data = request.get_json(force=True)
    target_role = (data.get("target_role") or "").strip()
    weeks_available = int(data.get("weeks_available") or 12)
    manual_skills = data.get("skills") or []

    if not target_role:
        return jsonify({"error": "target_role is required"}), 400

    db.get_or_create_student(
        db.get_student(student_id)["name"], db.get_student(student_id)["email"], target_role
    )

    resume = db.latest_resume(student_id)
    import json as _json
    resume_skills = _json.loads(resume["extracted_skills"]) if resume else []
    have_skills = sorted(set(resume_skills) | set(manual_skills))

    result = planner.run_full_pipeline(student_id, target_role, have_skills, weeks_available)
    return jsonify(result)


# --------------------------------------------------------- API: dashboard --
@app.route("/api/dashboard")
def api_dashboard():
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"error": "no active session — please onboard first"}), 401
    return jsonify(planner.get_dashboard(student_id))


# --------------------------------------------------------- API: progress ---
@app.route("/api/progress/update", methods=["POST"])
def api_progress_update():
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"error": "no active session — please onboard first"}), 401

    data = request.get_json(force=True)
    week_number = int(data.get("week_number"))
    milestone = data.get("milestone")
    status = data.get("status", "done")

    db.upsert_progress(student_id, week_number, milestone, status)
    progress = db.get_progress(student_id)
    return jsonify({"progress": progress})


@app.route("/api/system_status")
def api_system_status():
    return jsonify(planner.system_status())


if __name__ == "__main__":
    db.init_db()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
