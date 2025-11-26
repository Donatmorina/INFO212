from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, origins=["http://localhost:5173"]) 

DB_NAME = 'attendence.db'

# DATABASE SETUP 
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Users table with role
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Courses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_code TEXT NOT NULL,
            total_sessions INTEGER DEFAULT 0,
            compulsory_sessions INTEGER DEFAULT 0
        )
    ''')

    # Enrollments
    c.execute('''
        CREATE TABLE IF NOT EXISTS course_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            UNIQUE(student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')

    # Attendance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')

    # Ensure one TA user
    c.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
              ('admin', 'admin', 'ta'))

    conn.commit()
    conn.close()


# AUTHENTICATION
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, role FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        user_id, role = user
        return jsonify({"success": True, "user_id": user_id, "role": role})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401


@app.route('/api/create_account', methods=['POST'])
def api_create_account():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'student')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                  (username, password, role))
        if role == 'student':
            c.execute('INSERT OR IGNORE INTO students (name) VALUES (?)', (username,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Account created successfully"})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "message": "Username already exists"}), 409


# COURSES 
@app.route('/api/courses', methods=['GET', 'POST'])
def api_courses():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('course_name', '').strip()
        code = data.get('course_code', '').strip()
        total_sessions = int(data.get('total_sessions', 0))
        compulsory_sessions = int(data.get('compulsory_sessions', 0))
        compulsory_sessions = min(compulsory_sessions, total_sessions)
        if name and code:
            c.execute('''
                INSERT INTO courses (course_name, course_code, total_sessions, compulsory_sessions)
                VALUES (?, ?, ?, ?)
            ''', (name, code, total_sessions, compulsory_sessions))
            conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Course added"})
    else:
        c.execute('SELECT id, course_name, course_code, total_sessions, compulsory_sessions FROM courses')
        rows = c.fetchall()
        conn.close()
        courses = [
            {
                "id": r[0],
                "course_name": r[1],
                "course_code": r[2],
                "total_sessions": r[3],
                "compulsory_sessions": r[4],
            }
            for r in rows
        ]
        return jsonify(courses)


# STUDENTS 
@app.route('/api/students', methods=['GET'])
def api_get_students():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, name FROM students ORDER BY name')
    rows = c.fetchall()
    conn.close()
    students = [{"id": r[0], "name": r[1]} for r in rows]
    return jsonify(students)


# ENROLL STUDENT TO COURSE 
@app.route('/api/enroll', methods=['POST'])
def api_enroll_student():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if not (student_id and course_id):
        return jsonify({"success": False, "message": "Missing student_id or course_id"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(
            'INSERT OR IGNORE INTO course_enrollments (student_id, course_id) VALUES (?, ?)',
            (student_id, course_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Student enrolled successfully"})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


# STUDENTS IN COURSE 
@app.route('/api/course/<int:course_id>/students', methods=['GET'])
def api_get_course_students(course_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT s.id, s.name
        FROM course_enrollments ce
        JOIN students s ON ce.student_id = s.id
        WHERE ce.course_id = ?
        ORDER BY s.name
    ''', (course_id,))
    rows = c.fetchall()
    conn.close()

    students = [{"id": r[0], "name": r[1]} for r in rows]
    return jsonify(students)


# ATTENDANCE
@app.route('/api/attendance', methods=['POST'])
def api_attendance():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    date = data.get('date')
    status = data.get('status', 'Absent')

    if not (student_id and course_id and date):
        return jsonify({"success": False, "message": "Missing data"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO attendance (student_id, course_id, date, status) VALUES (?, ?, ?, ?)',
              (student_id, course_id, date, status))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Attendance recorded"})


@app.route('/api/student/<int:student_user_id>/attendance', methods=['GET'])
def api_get_student_attendance(student_user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Find username in users table
    c.execute('SELECT username FROM users WHERE id=?', (student_user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify([])

    username = row[0]

    # Find student-id in students table
    c.execute('SELECT id FROM students WHERE name=?', (username,))
    srow = c.fetchone()
    if not srow:
        conn.close()
        return jsonify([])

    real_student_id = srow[0]

    # 3) Get attendance + course_id
    c.execute('''
        SELECT a.date,
               a.status,
               c.course_name,
               c.course_code,
               c.id
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id=?
        ORDER BY a.date DESC
    ''', (real_student_id,))
    rows = c.fetchall()
    conn.close()

    attendance = [
        {
            "date": r[0],
            "status": r[1],
            "course_name": r[2],
            "course_code": r[3],
            "course_id": r[4],
        }
        for r in rows
    ]
    return jsonify(attendance)




@app.route('/api/course/<int:course_id>/attendance', methods=['GET'])
def api_course_attendance(course_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT a.id, a.date, s.name, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.course_id = ?
        ORDER BY a.date DESC, s.name ASC
    ''', (course_id,))
    rows = c.fetchall()
    conn.close()

    records = [
        {"id": r[0], "date": r[1], "student_name": r[2], "status": r[3]}
        for r in rows
    ]
    return jsonify(records)

@app.route('/api/attendance/<int:attendance_id>', methods=['PATCH'])
def api_update_attendance(attendance_id):
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ('Present', 'Absent', 'Excused'):
        return jsonify({"success": False, "message": "Invalid status"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE attendance SET status=? WHERE id=?', (new_status, attendance_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Attendance updated"})

@app.route('/api/course/<int:course_id>/summary', methods=['GET'])
def api_course_summary(course_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Get total/compulsory sessions
    c.execute('SELECT total_sessions, compulsory_sessions FROM courses WHERE id=?', (course_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Course not found"}), 404

    total_sessions, compulsory_sessions = row
    total_sessions = total_sessions or 0
    compulsory_sessions = compulsory_sessions or 0
    allowed_skips = max(0, total_sessions - compulsory_sessions)

    # Get recorded sessions
    c.execute('SELECT COUNT(DISTINCT date) FROM attendance WHERE course_id=?', (course_id,))
    sessions_recorded = c.fetchone()[0] or 0

    # Get attendance per student
    c.execute('''
        SELECT s.id, s.name,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count,
               SUM(CASE WHEN a.status = 'Absent'  THEN 1 ELSE 0 END) AS absent_count
        FROM course_enrollments ce
        JOIN students s ON ce.student_id = s.id
        LEFT JOIN attendance a
               ON a.student_id = s.id AND a.course_id = ce.course_id
        WHERE ce.course_id = ?
        GROUP BY s.id, s.name
        ORDER BY s.name
    ''', (course_id,))
    rows = c.fetchall()
    conn.close()

    students = []
    for sid, name, present_count, absent_count in rows:
        present_count = present_count or 0
        absent_count = absent_count or 0

        if sessions_recorded > 0:
            attendance_percent = round((present_count / sessions_recorded) * 100, 1)
        else:
            attendance_percent = 0

        remaining_skips = allowed_skips - absent_count
        if remaining_skips < 0:
            remaining_skips = 0

        students.append({
            "student_id": sid,
            "name": name,
            "present": present_count,
            "absent": absent_count,
            "attendance_percent": attendance_percent,
            "remaining_skips": remaining_skips
        })

    return jsonify({
        "course_id": course_id,
        "total_sessions": total_sessions,
        "compulsory_sessions": compulsory_sessions,
        "allowed_skips": allowed_skips,
        "sessions_recorded": sessions_recorded,
        "students": students
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
