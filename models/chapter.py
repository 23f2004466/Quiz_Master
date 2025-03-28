from . import db

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    chapter_description = db.Column(db.String(300), nullable=False)
    subject = db.relationship('Subject', back_populates='chapters')
    quizzes = db.relationship('Quiz', back_populates='chapter', cascade="all, delete-orphan")
