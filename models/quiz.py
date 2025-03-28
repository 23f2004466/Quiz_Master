from . import db
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_title = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_of_quiz = db.Column(db.Time, nullable=False)
    remarks = db.Column(db.String(1000), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    chapter = db.relationship('Chapter', back_populates='quizzes')
    questions = db.relationship('Question', back_populates='quiz', cascade="all, delete-orphan")
    scores = db.relationship('Score', back_populates='quiz')
