import matplotlib
from flask import current_app
matplotlib.use('Agg')
import os
import matplotlib.pyplot as plt 
from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash,request, session
from flask_login import login_required, current_user
from models.subject import Subject
from models.chapter import Chapter
from models.quiz import Quiz
from models.user import User
from models.score import Score
from models.question import Question
from models import db



admin_bp = Blueprint('admin', __name__)

# admin-acess decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Access Denied! Admins Only.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function



def generate_charts():
    """Generates bar and pie charts and saves them as images."""
    
    # fetching Data for Bar Chart (Average Scores)
    charts_dir = os.path.join(current_app.static_folder, "charts")
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
    quizzes = db.session.query(Quiz.quiz_title, db.func.avg(Score.total_score))\
                        .join(Score, Quiz.id == Score.quiz_id)\
                        .group_by(Quiz.id)\
                        .all()

    if quizzes:
        labels, scores = zip(*quizzes)

        plt.figure(figsize=(6, 4))
        plt.bar(labels, scores, color='royalblue')
        plt.ylabel("Average Score")
        plt.title("Average Scores per Quiz")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, "average_scores.png"))
        plt.close()
    
        quizzes = db.session.query(Quiz.quiz_title, db.func.count(Score.id))\
                        .join(Score, Quiz.id == Score.quiz_id)\
                        .filter(Score.completed == True)\
                        .group_by(Quiz.id)\
                        .all()

    print("Quiz Completion Data:", quizzes)  # Debugging print

    if quizzes:
        labels, counts = zip(*quizzes)
    else:
        labels, counts = ["No Data"], [1]  

    plt.figure(figsize=(5, 5))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0'])
    plt.title("Quiz Completion Rates")
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, "completion_rates.png"))
    plt.close()




@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    
    generate_charts()  # calling function to create charts
    return render_template('admin/admin_dashboard.html', 
                           bar_chart="static/charts/average_scores.png",
                           pie_chart="static/charts/completion_rates.png")

#fetch all subjects
@admin_bp.route('/manage_subject', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_subject():
    subjects = Subject.query.all()
    return render_template("admin/manage_subject.html", subjects=subjects)
   
    
# add a subject
@admin_bp.route('/add_subject', methods=['GET', 'POST'])
@login_required
@admin_required

def add_subject():
    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        new_subject = Subject(subject_name=subject_name)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('admin.manage_subject'))
    return redirect(url_for('admin.manage_subject'))
    

#edit a subject
@admin_bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if request.method == 'POST':
        subject.subject_name = request.form.get('subject_name')  # Updating the subject name
        db.session.commit()
        return redirect(url_for('admin.manage_subject'))
    return redirect(url_for('admin.manage_subject'))

# delete a subject
@admin_bp.route('/delete_subject/<int:subject_id>', methods=[ 'GET', 'POST'])
@login_required
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Subject not found", "danger")
        return "Subject not found"
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('admin.manage_subject'))

# add a chapter
@admin_bp.route("/add_chapter/<int:subject_id>", methods=[ "GET" ,'POST'])
@login_required
@admin_required
def add_chapter(subject_id):
    subject=Subject.query.get(subject_id)
    if request.method == 'POST':
        chapter_name = request.form.get('chapter_name')
        chapter_description = request.form.get('chapter_description')
        new_chapter = Chapter(chapter_name=chapter_name, chapter_description=chapter_description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
    
        return redirect(url_for('admin.manage_subject'))
    return redirect(url_for('admin.manage_subject'))
 
# edit a chapter
@admin_bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if request.method == 'POST':
        chapter.chapter_name = request.form.get('chapter_name')
        chapter.chapter_description = request.form.get('chapter_description')
        db.session.commit()
        return redirect(url_for('admin.manage_subject'))
    return redirect(url_for('admin.manage_subject'))
 
# Delete a chapter
@admin_bp.route('/delete_chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash("Chapter not found", "danger")
        return "Chapter not found"
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin.manage_subject'))

 
# Route to add a question to a quiz
@admin_bp.route("/add-question/<int:quiz_id>", methods=["POST"])
@login_required
@admin_required
def add_question(quiz_id):
    
    
    question_title = request.form.get('question_title')
   
    question_statement = request.form.get('question_statement')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4 = request.form.get('option4')
    correct_answer = request.form.get('correct_answer')
   
    question = Question(
        question_title=question_title,
        question_statement=question_statement,
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        correct_answer=correct_answer,
     
       
        quiz_id=quiz_id
    )
    db.session.add(question)
    db.session.commit()
    return redirect(url_for("admin.quiz_manage"))

# Route to edit a question
@admin_bp.route("/edit-question/<int:question_id>", methods=["POST"])
@login_required
@admin_required
def edit_question(question_id):
    
  
    question = Question.query.get(question_id)
   
    question.question_statement = request.form.get('question_statement')
    question.option1 = request.form.get('option1')
    question.option2 = request.form.get('option2')
    question.option3 = request.form.get('option3')
    question.option4 = request.form.get('option4')
    question.correct_answer = request.form.get('correct_answer')
    
    db.session.commit()
    return redirect(url_for("admin.quiz_manage"))

# Route to delete a question
@admin_bp.route("/delete-question/<int:question_id>")
@login_required
@admin_required
def delete_question(question_id):
    
  
    question = Question.query.get(question_id)
    if not question:
        flash("Question not found", "danger")
        return redirect(url_for("admin.quiz_manage"))  # can query by primary key sql 2.0
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("admin.quiz_manage"))

#route for searching subjects
@admin_bp.route('/search-subject', methods=['GET'])
@login_required
@admin_required

def search_subject():
    query = request.args.get('subject_name')
    if query:
        subjects = Subject.query.filter(Subject.subject_name.ilike(f'%{query}%')).all()
    else:
        subjects = Subject.query.all()
    return render_template('admin/manage_subject.html', subjects=subjects)



# route for managing quizzes
@admin_bp.route("/quiz-manage")
@login_required
@admin_required  # Only admin can access this route 
def quiz_manage():
    
    quizzes = Quiz.query.all()
    chapters=Chapter.query.all()
    return render_template("admin/quiz_manage.html", quizzes=quizzes, chapters=chapters)


# route to add a quiz
@admin_bp.route("/add-quiz", methods=["POST"])
@login_required
@admin_required
def add_quiz():
    
    print(request.form)
    
    quiz_title = request.form.get('quiz_title')
    chapter_id = request.form.get('chapter_id')
    date_of_quiz = request.form.get('date_of_quiz')
    time_of_quiz = request.form.get('time_of_quiz')
    remarks = request.form.get('remarks')
    duration = request.form.get('duration')

 #  Converting date and time to Python objects
    date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()
    time_of_quiz = datetime.strptime(time_of_quiz, '%H:%M').time()
    duration = int(duration) # convert duration to integer


    new_quiz = Quiz(quiz_title=quiz_title,chapter_id=chapter_id,date_of_quiz=date_of_quiz,time_of_quiz=time_of_quiz,remarks=remarks,
        duration=duration)
    
    db.session.add(new_quiz)
    db.session.commit()
    return redirect(url_for("admin.quiz_manage"))
    


# Route to edit a quiz
@admin_bp.route("/edit-quiz/<int:quiz_id>", methods=["POST"])
@login_required
@admin_required  

def edit_quiz(quiz_id):
    
    quiz = db.session.get(Quiz, quiz_id)
    quiz.quiz_title = request.form.get('quiz_title')
    
    db.session.commit()

    return redirect(url_for("admin.quiz_manage"))

# route to delete a quiz
@admin_bp.route("/delete-quiz/<int:quiz_id>")
@login_required
@admin_required  
def delete_quiz(quiz_id):
    
    quiz = db.session.get(Quiz, quiz_id) 
    if not quiz:
        flash("Quiz not found", "danger")
        return redirect(url_for("admin.quiz_manage")) 
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for("admin.quiz_manage"))

@admin_bp.route('/search-quiz', methods=['GET'])
@login_required
@admin_required
def search_quiz():
    query = request.args.get('quiz_title')
    if query:
        quizzes = Quiz.query.filter(Quiz.quiz_title.ilike(f'%{query}%')).all()
    else:
        quizzes = Quiz.query.all()
    return render_template('admin/quiz_manage.html', quizzes=quizzes)



@admin_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        user = User.query.get(user_id)
        if user:
            if action == "activate":
                user.is_active = True
                flash(f'User {user.username} activated.', 'success')
            elif action == "deactivate":
                user.is_active = False
                flash(f'User {user.username} deactivated.', 'warning')
            db.session.commit()
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/manage_users.html', users=users)
            



        
