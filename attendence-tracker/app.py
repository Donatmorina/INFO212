from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

DB_NAME = 'attendence.db'

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                status TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        ''')
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        # Add a default TA user
        c.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin', 'ta'))
        conn.commit()
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT id, role FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = username
            session['role'] = user[1]
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
            if role == 'student':
                # Add to students table if not already present
                c.execute('INSERT OR IGNORE INTO students (name) VALUES (?)', (username,))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Username already exists. Please choose another."
            conn.close()
    return render_template('create_account.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    user_id = session.get('user_id')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if role == 'ta':
        # TA can add students and mark attendance
        if request.method == 'POST' and 'student_name' in request.form:
            name = request.form['student_name']
            c.execute('INSERT OR IGNORE INTO students (name) VALUES (?)', (name,))
            conn.commit()
        if request.method == 'POST' and 'attendance_date' in request.form:
            attendance_date = request.form['attendance_date']
            for student_id in request.form.getlist('student_id'):
                status = request.form.get(f'status_{student_id}')
                c.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)',
                          (student_id, attendance_date, status))
                conn.commit()
        c.execute('SELECT id, name FROM students')
        students = c.fetchall()
        c.execute('''
            SELECT s.name, a.date, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            ORDER BY a.date DESC
        ''')
        history = c.fetchall()
        conn.close()
        return render_template('index.html', students=students, history=history, role=role)
    else:
        # Student: show only their own attendance history
        c.execute('SELECT id FROM students WHERE name=?', (session['user'],))
        student = c.fetchone()
        attendance_history = []
        if student:
            student_id = student[0]
            c.execute('SELECT date, status FROM attendance WHERE student_id=? ORDER BY date DESC', (student_id,))
            attendance_history = c.fetchall()
        conn.close()
        return render_template('student_dashboard.html', attendance_history=attendance_history, role=role)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
