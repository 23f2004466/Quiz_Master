from . import db
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    time_taken = db.Column(db.Time, nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='scores')
    quiz = db.relationship('Quiz', back_populates='scores')
