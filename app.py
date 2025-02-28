from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
from psycopg2 import sql
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_URL
from models import User, HealthMetric
from extensions import db
from dotenv import load_dotenv
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Database connection using environment variables
conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST')
)
cur = conn.cursor()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:irfan@localhost:5432/proxihealth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

print("Database tables created successfully!")

app.secret_key = os.getenv('SECRET_KEY', 'your_secure_fallback_secret_key')


app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Home route
@app.route('/home')
def home():
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/location-check')
def location_check():
    return render_template('location_check.html')

@app.route('/admin-panel')
def admin_panel():
    return render_template('admin_panel.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"Login attempt for email: {email}")  # Log the email being used for login
        cur.execute('SELECT * FROM "user" WHERE "email" = %s', (email,))

        user = cur.fetchone()

        if user and check_password_hash(user[3], password):  # Assuming hashed password is at index 3
            session['user_id'] = user[0]
            session['user_id'] = user[0]
            print(f"Session set for user ID: {session['user_id']}")  # Debug statement to check session
            session['user_id'] = user[0]
            print(f"Session set for user ID: {session['user_id']}")  # Debug statement to check session
            flash('Login successful!', 'success')


            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('home'))
    
    return render_template('login.html', title='Login')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    try:
        print(f"Inserting user: {username}, {email}")  # Log the data being inserted
        cur.execute("INSERT INTO user (username,email,password) VALUES (%s, %s, %s)", (username,email,hashed_password))
        conn.commit()
        # Retrieve the ID of the newly inserted user
        cur.execute("SELECT id FROM user WHERE email = %s", (email,))
        user_id = cur.fetchone()[0]
        print(f"Retrieved user ID: {user_id}")  # Debug statement to check the user ID

        session['user_id'] = user_id  # Set the session for the new user

        session['user_id'] = user_id  # Set the session for the new user
        print(f"Session set for new user ID: {session['user_id']}")  # Debug statement to check session
        session['user_id'] = user_id  # Set the session for the new user
        print(f"Session set for new user ID: {session['user_id']}")  # Debug statement to check session
        flash('Signup successful! You are now logged in.', 'success')


        return redirect(url_for('dashboard'))  # Redirect to dashboard or home

    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')

    return render_template('signup.html', title='Sign Up')

# Dashboard route
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('home'))
    return render_template('index.html', title='Dashboard')

# Health metrics submission endpoint
@app.route('/submit_health_metrics', methods=['GET', 'POST'])
def submit_health_metrics():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in first.', 'warning')
            return redirect(url_for('index'))

        heart_rate = request.form.get('heart_rate')
        step_count = request.form.get('step_count')
        sleep_duration = request.form.get('sleep_duration')

        try:
            new_metric = HealthMetric(
                user_id=user_id,
                heart_rate=heart_rate,
                step_count=step_count,
                sleep_duration=sleep_duration
            )
            db.session.add(new_metric)
            db.session.commit()
            flash('Health metrics submitted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}', 'danger')

        return redirect(url_for('index'))

    return render_template('submit_health_metrics.html')

@app.route('/view_health_metrics')
def view_health_metrics():
    user_id = session.get('user_id')
    print(f"User ID from session: {user_id}")
    if not user_id:
        flash('Please log in first.', 'warning')
        return redirect(url_for('home'))

    try:
        with conn.cursor() as cur:  # Using context manager
            cur.execute("""
                SELECT heart_rate, step_count, sleep_duration, timestamp
                FROM health_metric
                WHERE user_id = %s
                ORDER BY timestamp DESC;
            """, (user_id,))
            health_metrics = cur.fetchall()
    except Exception as e:
        flash(f'Error retrieving health metrics: {e}', 'danger')
        health_metrics = []

    return render_template('view_health_metrics.html', health_metrics=health_metrics)

# Logout endpoint
@app.route('/logout')
def logout():
    session.clear()
    session.pop('user_id', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
