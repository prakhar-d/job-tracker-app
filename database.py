import os
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash

# Get the database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    # Connect to PostgreSQL using the URL provided by Render
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # PostgreSQL uses SERIAL instead of AUTOINCREMENT
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            source TEXT,
            url TEXT UNIQUE,
            posted_date TEXT,
            category TEXT DEFAULT 'General',
            status TEXT DEFAULT 'Not Applied',
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    c.close()
    conn.close()


# =====================================
# User Auth Functions
# =====================================
def create_user(email, username, password):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        # PostgreSQL uses %s instead of ? for parameters
        c.execute('INSERT INTO users (email, username, password_hash) VALUES (%s, %s, %s)',
                   (email, username, password_hash))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False  # email already registered
    finally:
        c.close()
        conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = c.fetchone()
    c.close()
    conn.close()
    return user

def verify_password(identifier, password):
    """Checks if the identifier (email OR username) and password match."""
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if the identifier matches the email OR the username
    c.execute('SELECT * FROM users WHERE email = %s OR username = %s', (identifier, identifier))
    user = c.fetchone()
    c.close()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None


# =====================================
# Job Functions
# =====================================
def insert_job(title, company, location, source, url, posted_date, category='General'):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO jobs (title, company, location, source, url, posted_date, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (title, company, location, source, url, posted_date, category))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        c.close()
        conn.close()

def get_all_jobs(keyword=None, status=None, category=None):
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if keyword:
        query += " AND (title ILIKE %s OR company ILIKE %s)"
        params.extend([f'%{keyword}%', f'%{keyword}%'])

    if status and status != 'All':
        query += " AND status = %s"
        params.append(status)

    if category and category != 'All':
        query += " AND category = %s"
        params.append(category)

    query += " ORDER BY fetched_at DESC"

    c.execute(query, params)
    jobs = c.fetchall()
    c.close()
    conn.close()
    return jobs

def update_status(job_id, new_status):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE jobs SET status = %s WHERE id = %s", (new_status, job_id))
    conn.commit()
    c.close()
    conn.close()

def get_stats():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jobs")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Applied'")
    applied = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Interested'")
    interested = c.fetchone()[0]
    c.close()
    conn.close()
    return {'total': total, 'applied': applied, 'interested': interested}