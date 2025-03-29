from . import db
#question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_title = db.Column(db.String(100), nullable=False)
    question_statement = db.Column(db.String(300), nullable=False)
    option1 = db.Column(db.String(400), nullable=True)
    option2 = db.Column(db.String(400), nullable=True)
    option3 = db.Column(db.String(400), nullable=True)
    option4 = db.Column(db.String(400), nullable=True)
    correct_answer = db.Column(db.String(400), nullable=False)
    quiz = db.relationship('Quiz', back_populates='questions')
