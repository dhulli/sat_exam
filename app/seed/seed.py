from app import db
from app.models import Exam, Question

def seed_basic_exam():
    exam = Exam(title="SAT Quick Demo")
    db.session.add(exam); db.session.flush()
    questions = [
        Question(
            exam_id=exam.id, order_index=1,
            text="2 + 2 = ?", choice_a="1", choice_b="2", choice_c="3", choice_d="4", correct="D"
        ),
        Question(
            exam_id=exam.id, order_index=2,
            text="Select a vowel.", choice_a="B", choice_b="C", choice_c="A", choice_d="D", correct="C"
        ),
    ]
    db.session.add_all(questions)
    db.session.commit()
    return exam.id
