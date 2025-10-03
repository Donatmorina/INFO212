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
        
        # Check if username is empty
        if not username or not password:
            error = "Username and password are required"
            return render_template('create_account.html', error=error)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # First check if username already exists
            c.execute('SELECT username FROM users WHERE username=?', (username,))
            if c.fetchone():
                error = "Username already exists. Please choose another."
                conn.close()
                return render_template('create_account.html', error=error)
                
            # Insert new user
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                     (username, password, role))
            
            # If role is student, also add to students table
            if role == 'student':
                c.execute('INSERT OR IGNORE INTO students (name) VALUES (?)', (username,))
            
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
            
        except sqlite3.Error as e:
            error = f"Database error: {str(e)}"
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

# Student Attendance Tracker

This is a simple web application for tracking student attendance, supporting two user roles: **Teaching Assistant (TA)** and **Student**.  
- **Teaching Assistants** can add students and mark their attendance.
- **Students** can view their own attendance history.

## Features

- User authentication (login/logout)
- Create account as either TA or Student
- TA dashboard: add students, mark attendance, view all attendance records
- Student dashboard: view your own attendance history
- Role-based access control

## Folder Structure

```
attendence-tracker/
│
├── app.py
├── attendence.db (created automatically)
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── index.html
    ├── login.html
    ├── create_account.html
    └── student_dashboard.html
```

## Setup Instructions

1. **Install Python 3.12 or newer**  
   Download from [python.org](https://www.python.org/downloads/).

2. **Install Flask**  
   Open a terminal in the project folder and run:
   ```
   pip install flask
   ```

3. **(Optional) Clean up Python environment if you see warnings**  
   If you see warnings about "invalid distribution", you can ignore them if the app runs, or clean your environment as described [here](https://github.com/pypa/pip/issues/12063).

4. **Run the Application**  
   In the terminal, run:
   ```
   python app.py
   ```
   The app will start at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

5. **First-Time Database Setup**  
   The database (`attendence.db`) is created automatically the first time you run the app.

## Usage

### 1. Login / Create Account

- Go to `/login` to log in.
- Click "Create Account" to register as a TA or Student.
- Default TA account:  
  - Username: `admin`  
  - Password: `admin`

### 2. Teaching Assistant Dashboard

- Add new students by name.
- Mark attendance for any student for a selected date.
- View all attendance records.

### 3. Student Dashboard

- View your own attendance history (dates and status).
- You cannot mark attendance or see other students.

### 4. Logout

- Click "Logout" to return to the login page.

## Notes

- If you change the database schema, delete `attendence.db` and restart the app to recreate it.
- Passwords are stored in plain text for demonstration purposes. **Do not use this in production.**
- For any issues, check the terminal for error messages.

## License

This project is for educational purposes.
