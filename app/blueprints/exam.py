from flask import Blueprint, render_template

bp = Blueprint("exam", __name__, template_folder="../templates")

@bp.get("/take")
def take_exam():
    return render_template("exam.html")  # we'll add this later
