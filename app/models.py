from datetime import datetime
from flask_login import UserMixin
from . import db, login_manager

# ---------- Users ----------
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    attempts = db.relationship(
        "Attempt",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------- Exams ----------
class Exam(db.Model):
    __tablename__ = "exam"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    questions = db.relationship(
        "Question",
        back_populates="exam",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Question.order_index.asc()",
    )

    attempts = db.relationship(
        "Attempt",
        back_populates="exam",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ---------- Questions ----------
class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exam.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exam = db.relationship("Exam", back_populates="questions")

    # Optional ordering for stable rendering
    order_index = db.Column(db.Integer, nullable=False, default=0)

    text = db.Column(db.Text, nullable=False)
    choice_a = db.Column(db.Text, nullable=False)
    choice_b = db.Column(db.Text, nullable=False)
    choice_c = db.Column(db.Text, nullable=False)
    choice_d = db.Column(db.Text, nullable=False)

    # 'A', 'B', 'C', or 'D'
    correct = db.Column(db.String(1), nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "correct in ('A','B','C','D')",
            name="ck_question_correct_is_valid_choice",
        ),
    )


# ---------- Attempts ----------
class Attempt(db.Model):
    __tablename__ = "attempt"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user = db.relationship("User", back_populates="attempts")

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exam.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exam = db.relationship("Exam", back_populates="attempts")

    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)

    # raw score (# correct). Keep it denormalized for fast display.
    raw = db.Column(db.Integer, nullable=False, default=0)

    answers = db.relationship(
        "AttemptAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Optional: prevent duplicate active attempts if you want one-at-a-time per user/exam.
    # __table_args__ = (db.UniqueConstraint("user_id", "exam_id", name="uq_attempt_user_exam"),)


# ---------- AttemptAnswers ----------
class AttemptAnswer(db.Model):
    __tablename__ = "attempt_answer"
    id = db.Column(db.Integer, primary_key=True)

    attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("attempt.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt = db.relationship("Attempt", back_populates="answers")

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("question.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # We don’t need full relationship to Question for MVP, but you can add it:
    # question = db.relationship("Question")

    # Selected choice: 'A'/'B'/'C'/'D'
    selected = db.Column(db.String(1), nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "selected in ('A','B','C','D')",
            name="ck_attempt_answer_selected_is_valid_choice",
        ),
        db.UniqueConstraint(
            "attempt_id", "question_id",
            name="uq_attempt_answer_attempt_question",
        ),
    )
