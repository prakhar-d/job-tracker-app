import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from database import (init_db, get_all_jobs, update_status, get_stats,
                       create_user, verify_password, get_user_by_id)
from fetch_jobs import fetch_all

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
init_db()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Basic email format check
EMAIL_REGEX = re.compile(r'^[\w\.\+\-]+\@[\w\-]+\.[a-zA-Z]{2,}$')

# Password: at least 6 chars, 1 uppercase, 1 digit, 1 special character
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>_\-+=~`\[\];\'/\\]).{6,}$')


class User(UserMixin):
    def __init__(self, user_row):
        self.id = user_row['id']
        self.email = user_row['email']
        self.username = user_row['username']


@login_manager.user_loader
def load_user(user_id):
    user_row = get_user_by_id(user_id)
    if user_row:
        return User(user_row)
    return None


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        username = request.form['username'].strip()
        password = request.form['password']

        if not email or not password or not username:
            flash('All fields are required.')
            return redirect(url_for('signup'))

        if not EMAIL_REGEX.match(email):
            flash('Please enter a valid email address.')
            return redirect(url_for('signup'))

        if not PASSWORD_REGEX.match(password):
            flash('Password must be at least 6 characters and include one '
                  'uppercase letter, one number, and one special character.')
            return redirect(url_for('signup'))

        success = create_user(email, username, password)
        if success:
            flash('Account created! Please log in.')
            return redirect(url_for('login'))
        else:
            flash('An account with this email already exists.')
            return redirect(url_for('signup'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user_row = verify_password(email, password)
        if user_row:
            login_user(User(user_row))
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def home():
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', 'All')
    category = request.args.get('category', 'All')

    jobs = get_all_jobs(keyword=keyword if keyword else None, 
                        status=status, 
                        category=category)
    stats = get_stats()

    return render_template('index.html', jobs=jobs, stats=stats,
                            keyword=keyword, status=status, category=category)


@app.route('/update/<int:job_id>/<new_status>')
@login_required
def update(job_id, new_status):
    update_status(job_id, new_status)
    return redirect(url_for('home'))


@app.route('/refresh')
@login_required
def refresh():
    fetch_all()
    return redirect(url_for('home'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)