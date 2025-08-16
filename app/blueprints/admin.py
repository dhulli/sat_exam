import io, csv, json
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .. import db
from ..models import Exam, Question

bp = Blueprint("admin", __name__, template_folder="../templates")

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))
        if not getattr(current_user, "is_admin", False):
            flash("Admin access required.")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

@bp.get("/upload")
@login_required
@admin_required
def upload_form():
    return render_template("admin_upload.html")

@bp.post("/upload")
@login_required
@admin_required
def upload_post():
    title = (request.form.get("title") or "").strip()
    file = request.files.get("file")

    if not title:
        flash("Title is required.")
        return redirect(url_for("admin.upload_form"))
    if not file or file.filename == "":
        flash("Choose a .csv or .json file.")
        return redirect(url_for("admin.upload_form"))
    if Exam.query.filter_by(title=title).first():
        flash("An exam with this title already exists.")
        return redirect(url_for("admin.upload_form"))

    questions = []
    try:
        name = file.filename.lower()
        if name.endswith(".csv"):
            data = file.read().decode("utf-8-sig")
            f = io.StringIO(data)
            reader = csv.DictReader(f)
            required = {"order_index","text","choice_a","choice_b","choice_c","choice_d","correct"}
            headers = {h.strip() for h in (reader.fieldnames or [])}
            if not required.issubset(headers):
                flash("CSV headers must be: " + ", ".join(sorted(required)))
                return redirect(url_for("admin.upload_form"))
            for row in reader:
                questions.append(Question(
                    order_index=int(row.get("order_index") or 0),
                    text=(row["text"] or "").strip(),
                    choice_a=(row["choice_a"] or "").strip(),
                    choice_b=(row["choice_b"] or "").strip(),
                    choice_c=(row["choice_c"] or "").strip(),
                    choice_d=(row["choice_d"] or "").strip(),
                    correct=(row["correct"] or "").strip().upper(),
                ))
        elif name.endswith(".json"):
            payload = json.load(file)
            # Accept {"title": "...", "questions":[...]} or just a list of questions
            qs = payload.get("questions") if isinstance(payload, dict) else payload
            for i, q in enumerate(qs, start=1):
                questions.append(Question(
                    order_index=int(q.get("order_index") or i),
                    text=(q["text"] or "").strip(),
                    choice_a=(q.get("choice_a") or q.get("choices",{}).get("A","")).strip(),
                    choice_b=(q.get("choice_b") or q.get("choices",{}).get("B","")).strip(),
                    choice_c=(q.get("choice_c") or q.get("choices",{}).get("C","")).strip(),
                    choice_d=(q.get("choice_d") or q.get("choices",{}).get("D","")).strip(),
                    correct=(q.get("correct") or "").strip().upper(),
                ))
        else:
            flash("Unsupported file type. Use .csv or .json.")
            return redirect(url_for("admin.upload_form"))
    except Exception as e:
        flash(f"Failed to parse file: {e}")
        return redirect(url_for("admin.upload_form"))

    if not questions:
        flash("No questions parsed.")
        return redirect(url_for("admin.upload_form"))

    exam = Exam(title=title)
    db.session.add(exam); db.session.flush()
    for q in questions:
        q.exam_id = exam.id
    db.session.add_all(questions)
    db.session.commit()

    flash(f"Uploaded exam '{title}' with {len(questions)} questions.")
    return redirect(url_for("index"))
