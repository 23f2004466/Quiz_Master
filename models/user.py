from flask_login import UserMixin
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='user')  # Default role = "user"
    qualification = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # if user is active or not
    scores = db.relationship('Score', back_populates='user')  # this scores will fetch all the score related to the particular user
    time_stamp = db.Column(db.DateTime, default=lambda: datetime.now(), nullable=False) #lambda: datetime.now() har naye user ke liye alag-alag timestamp store karega.


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)  # Flask-Login requires a string ID

    def is_admin(self):
        return self.role == 'admin'  # Returns True if user is admin

