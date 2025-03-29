from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

db = SQLAlchemy()
from .user import User
from .subject import Subject
from .chapter import Chapter
from .quiz import Quiz
from .question import Question
from .score import Score

def create_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin',password=generate_password_hash('admin@123', method='pbkdf2:sha256'),
        fullname='Admin',
            qualification='BS',
            dob=datetime.strptime('2005-03-11', '%Y-%m-%d').date(),
            role='admin') 
        
        db.session.add(admin)
        db.session.commit()
    return admin