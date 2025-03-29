import matplotlib.pyplot as plt 
from sqlalchemy.sql import func
from flask import Blueprint, render_template, request,flash,redirect, url_for
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
    query = Quiz.query.join(Chapter).join(Subject)  
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')
        if subject_id:
            query = query.filter(Subject.id == subject_id)   
        if chapter_id:

            query = query.filter(Chapter.id == chapter_id) 
    quizzes = query.filter(Quiz.questions.any()).all()


    return render_template('user/view_quiz.html', subjects=subjects, chapters=chapters, quizzes=quizzes, user=current_user)


@user_bp.route('/searching_quiz', methods=['GET'])
@login_required
def searching_quiz():
    subject_name = request.args.get('subject_name', '')
    query = Quiz.query.join(Chapter).join(Subject).filter(Subject.subject_name.ilike(f'%{subject_name}%'))
    quizzes = query.all()
    return render_template('user/view_quiz.html', subjects=Subject.query.all(), chapters=Chapter.query.all(), quizzes=quizzes, user=current_user)

@user_bp.route('/quiz_start', methods=['GET', 'POST'])
@login_required
def quiz_start():
    
    quiz_id=request.args.get('quiz_id')
    if quiz_id is None:
        return redirect(url_for('user.view_quiz'))
    quiz=Quiz.query.get(quiz_id)
    if not quiz:
        flash("Quiz not found", "danger")
        return redirect(url_for('user.view_quiz'))

    questions=Question.query.filter_by(quiz_id=quiz.id).all()
    time=quiz.time_of_quiz.hour*60+quiz.time_of_quiz.minute
    if request.method == 'POST':
        score=0
        for question in questions:
            user_answer = request.form.get(f'question-{question.id}')
            if user_answer == question.correct_answer:
                score += 1
        time_taken=datetime.now().time()  #store in hh;mm;ss format as db.Time is used 
        score=Score(quiz_id=quiz.id,user_id=current_user.id,time_taken=time_taken,total_score=score)
        db.session.add(score)
        db.session.commit()
        flash('Quiz Submitted successfully', 'success')
        return redirect(url_for("user.user_dashboard"))
    return render_template('user/quiz_start.html', quiz=quiz, questions=questions, time=time, user=current_user)

