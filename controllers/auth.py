from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models import db
from datetime import datetime


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error in home(): {e}")
        flash("An error occurred while loading the home page.", "danger")
        return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            if user.is_admin():
                return redirect(url_for('admin.admin_dashboard'))
            return redirect(url_for('user.user_dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')

        if not username or not password or not full_name or not qualification or not dob:
            flash("All fields are required!", "danger")
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken.", "danger")
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            fullname=full_name,
            qualification=qualification,
            dob=datetime.strptime(dob, '%Y-%m-%d').date()
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
