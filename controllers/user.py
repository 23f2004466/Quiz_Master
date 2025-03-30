import matplotlib
from flask import current_app

matplotlib.use('Agg')
import os
import matplotlib.pyplot as plt 
from sqlalchemy.sql import func
from flask import Blueprint, render_template, request,flash,redirect, url_for,session
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
    total_scores = db.session.query(func.sum(Score.total_score)).filter(Score.user_id==current_user.id).scalar() or 0
    total_attempts = db.session.query(func.count(Score.id)).filter(Score.user_id==current_user.id).scalar()
    scores = Score.query.filter(Score.user_id==current_user.id).all()

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
            print(f"Current User ID: {current_user.id}")
            query = query.filter(Subject.id == subject_id)   
        if chapter_id:

            query = query.filter(Chapter.id == chapter_id) 
    quizzes = query.filter(Quiz.questions.any()).all()
#c
    user_scores = {score.quiz_id: score for score in Score.query.filter_by(user_id=current_user.id).all()}
    for quiz in quizzes:
        quiz.user_score = user_scores.get(quiz.id)



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
            print(user_answer,question.correct_answer)
            if user_answer == question.correct_answer:
                score += 1
        time_taken=datetime.now().time()  #store in hh;mm;ss format as db.Time is used 
        score=Score(quiz_id=quiz.id,user_id=current_user.id,time_taken=time_taken,total_score=score,completed=True)
        db.session.add(score)
        db.session.commit()
        flash('Quiz Submitted successfully', 'success')
        return redirect(url_for("user.user_dashboard"))
    return render_template('user/quiz_start.html', quiz=quiz, questions=questions, time=time, user=current_user)

@user_bp.route('/user_summary')
@login_required
def user_summary():
    # fetch user Quiz data
    user_scores = (
        db.session.query(Chapter.chapter_name, db.func.sum(Score.total_score), db.func.count(Score.id))
        .join(Quiz, Quiz.id == Score.quiz_id)
        .join(Chapter, Chapter.id == Quiz.chapter_id)
        .filter(Score.user_id == current_user.id)
        .group_by(Chapter.chapter_name)
        .all()
    )
    if not user_scores:
        return render_template("user/user_summary.html", score_chart_url=None, attempt_chart_url=None)


    # data extraction
    chapters = [row[0] for row in user_scores]
    total_scores = [row[1] for row in user_scores]
    attempt_counts = [row[2] for row in user_scores]

   #static folder path
    charts_dir = os.path.join(current_app.static_folder, "charts")
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)

    score_chart_path= None
    attempt_chart_path = None

    if any(total_scores):
        plt.figure(figsize=(8, 5))
        plt.bar(chapters, total_scores, color='skyblue')
        plt.ylabel("Total Score")
        plt.xlabel("Chapters")
        plt.title(f"{current_user.username} - Total Score by Chapter")
        plt.xticks(rotation=45)
        plt.tight_layout()
        score_chart_path = os.path.join(charts_dir, f"{current_user.id}_score_chart.png")
        plt.savefig(score_chart_path)
        plt.close()

    if sum(attempt_counts) == 0:
        attempt_counts = [1] * len(chapters)  #excludes division by zero error
#pie chart
    if sum(attempt_counts)>0:
        plt.figure(figsize=(6, 6))
        plt.pie(attempt_counts, labels=chapters, autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
        plt.title(f"{current_user.username} - Quiz Attempts Distribution")
        attempt_chart_path = os.path.join(charts_dir, f"{current_user.id}_attempt_chart.png")
        plt.savefig(attempt_chart_path)
        plt.close()

    raw_leaderboard = db.session.query(User.username, db.func.sum(Score.total_score).label('total_score'))\
        .join(Score, User.id == Score.user_id)\
        .group_by(User.id)\
        .order_by(db.desc('total_score'))\
        .limit(5)\
        .all()

    leaderboard = [{"rank": idx + 1, "username": lb[0], "total_score": lb[1]} for idx, lb in enumerate(raw_leaderboard)]
    


    return render_template(
        "user/user_summary.html",user=current_user,
        score_chart_url=f"/static/charts/{current_user.id}_score_chart.png" if score_chart_path else None,
        attempt_chart_url=f"/static/charts/{current_user.id}_attempt_chart.png" if attempt_chart_path else None,
        leaderboard=leaderboard)
    
