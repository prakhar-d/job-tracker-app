import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = 'jobs.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            source TEXT,
            url TEXT UNIQUE,
            posted_date TEXT,
            category TEXT DEFAULT 'General',
            status TEXT DEFAULT 'Not Applied',
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


# =====================================
# User Auth Functions
# =====================================
def create_user(email, username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)',
                   (email, username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # email already registered
    finally:
        conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def verify_password(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None


# =====================================
# Job Functions
# =====================================
def insert_job(title, company, location, source, url, posted_date, category='General'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO jobs (title, company, location, source, url, posted_date, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, company, location, source, url, posted_date, category))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_jobs(keyword=None, status=None, category=None):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if keyword:
        query += " AND (title LIKE ? OR company LIKE ?)"
        params.extend([f'%{keyword}%', f'%{keyword}%'])

    if status and status != 'All':
        query += " AND status = ?"
        params.append(status)

    if category and category != 'All':
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY fetched_at DESC"

    c.execute(query, params)
    jobs = c.fetchall()
    conn.close()
    return jobs

def update_status(job_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jobs")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Applied'")
    applied = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Interested'")
    interested = c.fetchone()[0]
    conn.close()
    return {'total': total, 'applied': applied, 'interested': interested}