from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..models import User

bp = Blueprint("auth", __name__, template_folder="../templates")

def _is_safe_url(target: str) -> bool:
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return (test.scheme in {"http", "https"}) and (ref.netloc == test.netloc)

@bp.get("/login")
def login():
    nxt = request.args.get("next")
    return render_template("login.html", next=nxt)

@bp.post("/login")
def login_post():
    email = (request.form.get("email") or "").strip().lower()
    pw = request.form.get("password") or ""
    nxt = request.form.get("next")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, pw):
        flash("Invalid email or password.")
        # preserve next on failure
        return redirect(url_for("auth.login", next=nxt) if nxt else url_for("auth.login"))

    login_user(user)
    if nxt and _is_safe_url(nxt):
        return redirect(nxt)
    return redirect(url_for("index"))

@bp.get("/register")
def register():
    return render_template("register.html")

@bp.post("/register")
def register_post():
    email = (request.form.get("email") or "").strip().lower()
    pw = request.form.get("password") or ""

    if not email or not pw or len(pw) < 6:
        flash("Enter a valid email and a password with at least 6 characters.")
        return redirect(url_for("auth.register"))

    if User.query.filter_by(email=email).first():
        flash("Email already registered.")
        return redirect(url_for("auth.register"))

    user = User(email=email, password_hash=generate_password_hash(pw))
    db.session.add(user); db.session.commit()
    login_user(user)
    return redirect(url_for("index"))

@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Signed out.")
    return redirect(url_for("index"))
