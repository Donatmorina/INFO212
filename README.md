# Student Attendance Tracker INFO212

A simple web application for tracking student attendance, supporting two user roles: **Teaching Assistant (TA)** and **Student**.

## Features

- User authentication (login/logout)
- Create account as either TA or Student
- TA dashboard: add students, mark attendance, view all attendance records
- Student dashboard: view your own attendance history

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

3. **Run the Application**  
   In the terminal, run:
   ```
   python app.py
   ```
   The app will start at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

4. **First-Time Database Setup**  
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
- Passwords are stored in plain text for demonstration purposes. 

- Test