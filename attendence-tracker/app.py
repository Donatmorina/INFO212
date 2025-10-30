from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'attendence.db'

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

    # Students table (student records linked to student users)
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Courses table (includes total_sessions and compulsory_sessions)
    c.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_code TEXT NOT NULL,
            total_sessions INTEGER DEFAULT 0,
            compulsory_sessions INTEGER DEFAULT 0
        )
    ''')

    # If the table existed before without the new columns, add them
    c.execute("PRAGMA table_info(courses)")
    cols = [row[1] for row in c.fetchall()]
    if 'total_sessions' not in cols:
        try:
            c.execute('ALTER TABLE courses ADD COLUMN total_sessions INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass
    if 'compulsory_sessions' not in cols:
        try:
            c.execute('ALTER TABLE courses ADD COLUMN compulsory_sessions INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass

    # Course enrollments
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

    # Attendance table (records per student per course)
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

    # Ensure at least one TA account exists
    c.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin', 'ta'))

    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT id, role FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = username
            session['user_id'] = user[0]
            session['role'] = user[1]
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role = request.form.get('role', 'student')
        if not username or not password:
            error = 'Username and password required'
        else:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
                # If role is student, create a student record (if not exists)
                if role == 'student':
                    c.execute('INSERT OR IGNORE INTO students (name) VALUES (?)', (username,))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = 'Username already exists'
                conn.close()
    return render_template('create_account.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if role == 'ta':
        # determine selected course (works for GET and POST)
        selected_course = request.values.get('selected_course')

        # Create course (now with total_sessions and compulsory_sessions)
        if request.method == 'POST' and 'course_name' in request.form and 'course_code' in request.form:
            course_name = request.form['course_name'].strip()
            course_code = request.form['course_code'].strip()
            try:
                total_sessions = int(request.form.get('total_sessions', 0))
            except ValueError:
                total_sessions = 0
            try:
                compulsory_sessions = int(request.form.get('compulsory_sessions', 0))
            except ValueError:
                compulsory_sessions = 0
            # ensure compulsory is not greater than total
            if compulsory_sessions > total_sessions:
                compulsory_sessions = total_sessions
            if course_name and course_code:
                c.execute('INSERT INTO courses (course_name, course_code, total_sessions, compulsory_sessions) VALUES (?, ?, ?, ?)',
                          (course_name, course_code, total_sessions, compulsory_sessions))
                conn.commit()

        # Enroll student
        if request.method == 'POST' and request.form.get('enroll_student') is not None:
            student_id = request.form.get('student_id')
            course_id = request.form.get('course_id')
            if student_id and course_id:
                try:
                    c.execute('INSERT OR IGNORE INTO course_enrollments (student_id, course_id) VALUES (?, ?)', (student_id, course_id))
                    conn.commit()
                except sqlite3.IntegrityError:
                    pass

        # Mark attendance for selected course
        if request.method == 'POST' and 'attendance_date' in request.form and 'selected_course' in request.form:
            attendance_date = request.form['attendance_date']
            selected_course = request.form['selected_course']
            # only mark attendance for students explicitly checked by the TA
            selected_students = request.form.getlist('selected_student')
            for student_id in selected_students:
                status = request.form.get(f'status_{student_id}', 'Absent')
                if student_id and selected_course:
                    c.execute('INSERT INTO attendance (student_id, course_id, date, status) VALUES (?, ?, ?, ?)',
                              (student_id, selected_course, attendance_date, status))
            conn.commit()

        # Fetch course list (include total_sessions and compulsory_sessions)
        c.execute('SELECT id, course_name, course_code, total_sessions, compulsory_sessions FROM courses ORDER BY course_name')
        courses = c.fetchall()

        # Course info and students for the selected course
        course_info = None
        students = []
        if selected_course:
            # get course totals
            c.execute('SELECT total_sessions, compulsory_sessions FROM courses WHERE id=?', (selected_course,))
            course_row = c.fetchone()
            if course_row:
                total_sessions, compulsory_sessions = course_row
            else:
                total_sessions = 0
                compulsory_sessions = 0
            allowed_skips = max(0, (total_sessions or 0) - (compulsory_sessions or 0))
            course_info = {
                'total_sessions': total_sessions,
                'compulsory_sessions': compulsory_sessions,
                'allowed_skips': allowed_skips
            }

            # fetch enrolled students and compute absences + remaining skips
            c.execute('''
                SELECT s.id, s.name
                FROM course_enrollments ce
                JOIN students s ON ce.student_id = s.id
                WHERE ce.course_id = ?
                ORDER BY s.name
            ''', (selected_course,))
            enrolled = c.fetchall()
            students = []
            for sid, sname in enrolled:
                c.execute('SELECT COUNT(*) FROM attendance WHERE student_id=? AND course_id=? AND status=?', (sid, selected_course, 'Absent'))
                abs_count = c.fetchone()[0] or 0
                remaining = allowed_skips - abs_count
                if remaining < 0:
                    remaining = 0
                students.append((sid, sname, abs_count, remaining))

        # For enrollment dropdowns we still need all students
        c.execute('SELECT id, name FROM students ORDER BY name')
        all_students = c.fetchall()

        # Fetch enrollments for display
        c.execute('''
            SELECT s.name, c.course_name, c.course_code
            FROM course_enrollments ce
            JOIN students s ON ce.student_id = s.id
            JOIN courses c ON ce.course_id = c.id
            ORDER BY s.name
        ''')
        enrollments = c.fetchall()
        conn.close()
        return render_template('index.html',
                               students=students,
                               all_students=all_students,
                               courses=courses,
                               enrollments=enrollments,
                               selected_course=selected_course,
                               course_info=course_info,
                               role=role)

    else:
        # Student view: allow selecting a course to view attendance for
        username = session.get('user')
        c.execute('SELECT id FROM students WHERE name=?', (username,))
        row = c.fetchone()
        attendance_history = []
        courses = []
        selected_course = request.values.get('selected_course')  # works for GET form submit

        if row:
            student_id = row[0]

            # fetch courses the student is enrolled in
            c.execute('''
                SELECT c.id, c.course_name, c.course_code
                FROM course_enrollments ce
                JOIN courses c ON ce.course_id = c.id
                WHERE ce.student_id=?
                ORDER BY c.course_name
            ''', (student_id,))
            courses = c.fetchall()

            if selected_course:
                # ensure selected_course is int-like
                try:
                    sc_id = int(selected_course)
                except (ValueError, TypeError):
                    sc_id = None

                if sc_id:
                    # course totals
                    c.execute('SELECT total_sessions, compulsory_sessions FROM courses WHERE id=?', (sc_id,))
                    crow = c.fetchone()
                    if crow:
                        total_sessions, compulsory_sessions = crow
                    else:
                        total_sessions = 0
                        compulsory_sessions = 0
                    allowed_skips = max(0, (total_sessions or 0) - (compulsory_sessions or 0))

                    # student's attendance for that course
                    c.execute('''
                        SELECT a.date, a.status, c.course_name, c.course_code
                        FROM attendance a
                        LEFT JOIN courses c ON a.course_id = c.id
                        WHERE a.student_id=? AND a.course_id=?
                        ORDER BY a.date DESC
                    ''', (student_id, sc_id))
                    attendance_history = c.fetchall()

                    # count absences
                    c.execute('SELECT COUNT(*) FROM attendance WHERE student_id=? AND course_id=? AND status=?', (student_id, sc_id, 'Absent'))
                    abs_count = c.fetchone()[0] or 0
                    remaining_skips = allowed_skips - abs_count
                    if remaining_skips < 0:
                        remaining_skips = 0

                    course_info = {
                        'total_sessions': total_sessions,
                        'compulsory_sessions': compulsory_sessions,
                        'allowed_skips': allowed_skips,
                        'absences': abs_count,
                        'remaining_skips': remaining_skips
                    }
                else:
                    attendance_history = []
                    course_info = None
            else:
                # no course selected -> empty history (student must choose)
                attendance_history = []
                course_info = None

        conn.close()
        return render_template('student_dashboard.html',
                               attendance_history=attendance_history,
                               courses=courses,
                               selected_course=selected_course,
                               course_info=course_info,
                               role=role)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
