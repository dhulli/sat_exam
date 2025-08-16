from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("exam", __name__, template_folder="../templates")

@bp.get("/take")
@login_required
def take_exam():
    return render_template("exam.html")
