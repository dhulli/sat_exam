from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .. import db
from ..models import Exam, Question, Attempt, AttemptAnswer

bp = Blueprint("exam", __name__, template_folder="../templates")

def _get_owned_attempt_or_404(attempt_id: int) -> Attempt:
    attempt = Attempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        abort(403)
    return attempt

@bp.get("/")
@login_required
def list_exams():
    # List available exams
    exams = Exam.query.order_by(Exam.created_at.desc()).all()
    return render_template("exam_list.html", exams=exams)

@bp.post("/start")
@login_required
def start():
    # Create a new attempt for the chosen exam
    exam_id = request.form.get("exam_id", type=int)
    exam = Exam.query.get_or_404(exam_id)
    if not exam.questions:
        flash("This exam has no questions yet.")
        return redirect(url_for("exam.list_exams"))
    attempt = Attempt(user_id=current_user.id, exam_id=exam.id)
    db.session.add(attempt)
    db.session.commit()
    return redirect(url_for("exam.take_attempt", attempt_id=attempt.id))

@bp.get("/take/<int:attempt_id>")
@login_required
def take_attempt(attempt_id: int):
    # Render questions for this attempt
    attempt = _get_owned_attempt_or_404(attempt_id)
    exam = attempt.exam
    questions = exam.questions  # ordered by relationship
    return render_template("exam_take.html", attempt=attempt, exam=exam, questions=questions)

@bp.post("/submit/<int:attempt_id>")
@login_required
def submit_attempt(attempt_id: int):
    # Grade and store answers
    attempt = _get_owned_attempt_or_404(attempt_id)
    questions = attempt.exam.questions

    # idempotent: clear existing answers if resubmitted
    AttemptAnswer.query.filter_by(attempt_id=attempt.id).delete()

    valid = {"A", "B", "C", "D"}
    raw = 0
    for q in questions:
        choice = (request.form.get(f"q_{q.id}") or "").upper()
        if choice in valid:
            if choice == q.correct:
                raw += 1
            db.session.add(AttemptAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected=choice
            ))

    attempt.raw = raw
    attempt.completed_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("exam.result", attempt_id=attempt.id))

@bp.get("/result/<int:attempt_id>")
@login_required
def result(attempt_id: int):
    # Show score + per-question feedback
    attempt = _get_owned_attempt_or_404(attempt_id)
    exam = attempt.exam
    answers = {
        a.question_id: a.selected
        for a in AttemptAnswer.query.filter_by(attempt_id=attempt.id).all()
    }
    questions = exam.questions
    total = len(questions)
    return render_template(
        "exam_result.html",
        attempt=attempt, exam=exam,
        questions=questions, answers=answers, total=total
    )
