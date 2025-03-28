import matplotlib.pyplot as plt 
from sqlalchemy.sql import func
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models.user import User
from models.score import Score
from models.quiz import Quiz
from models.chapter import Chapter
from models.subject import Subject
from models.question import Question
from models import db
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/user_dashboard')
@login_required
def user_dashboard():
    total_scores = db.session.query(func.sum(Score.total_score)).filter_by(user_id=current_user.id).scalar() or 0
    total_attempts = db.session.query(func.count(Score.id)).filter_by(user_id=current_user.id).scalar()
    scores = Score.query.filter_by(user_id=current_user.id).all()

    average_score = total_scores / total_attempts if total_attempts > 0 else 0
    
    return render_template("user/user_dashboard.html", total_attempts=total_attempts, average_score=average_score, scores=scores,user=current_user)

@user_bp.route('/view_quiz', methods=['GET', 'POST'])
@login_required
def view_quiz():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()

    query = Quiz.query.join(Chapter).join(Subject)  # Correctly linking tables

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')

        if subject_id:
            query = query.filter(Subject.id == subject_id)  # Filter by subject
        if chapter_id:
            query = query.filter(Chapter.id == chapter_id)  # Filter by chapter

    quizzes = query.all()

    return render_template('user/view_quiz.html', subjects=subjects, chapters=chapters, quizzes=quizzes, user=current_user)


