from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB_NAME = 'attendence.db'  # Changed to match your actual file name

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # Students table
        c.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        # Attendance table
        c.execute('''
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                status TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Add student
    if request.method == 'POST' and 'student_name' in request.form:
        name = request.form['student_name']
        c.execute('INSERT INTO students (name) VALUES (?)', (name,))
        conn.commit()
    
    # Mark attendance
    if request.method == 'POST' and 'attendance_date' in request.form:
        attendance_date = request.form['attendance_date']
        for student_id in request.form.getlist('student_id'):
            status = request.form.get(f'status_{student_id}')
            c.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)',
                      (student_id, attendance_date, status))
            conn.commit()
    
    c.execute('SELECT id, name FROM students')
    students = c.fetchall()

    # Attendance history
    c.execute('''
        SELECT s.name, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC
    ''')
    history = c.fetchall()

    conn.close()
    return render_template('index.html', students=students, history=history)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
