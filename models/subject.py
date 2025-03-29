from . import db
#subject model
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    chapters = db.relationship('Chapter', back_populates='subject', cascade="all, delete-orphan")
