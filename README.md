# Student Attendance Tracker – INFO212

A fullstack web application for tracking student attendance, with separate dashboards for **Teaching Assistants (TAs)** and **Students**. The system is built using a Flask backend and a React (Vite) frontend.

---

## Features

- Login system with role-based access (TA / Student)
- TA dashboard:
  - Add new courses
  - Enroll students into courses
  - Mark attendance for each date
  - View course attendance history
  - View course summary (present/absent/percent)
- Student dashboard:
  - View attendance across all courses
  - Filter by course
  - View present/absent totals and attendance percentage
- SQLite database for persistent storage
- REST API using Flask
- Frontend built with React and Tailwind CSS

---

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

---

## Tools and Technologies Used

- MVC architecture  
- SQLite  
- Python (Flask backend)  
- Node.js / Vite (React frontend)  
- Tailwind CSS for styling  
- Axios for handling API requests between frontend and backend  
- GitHub for version control and coordination  
- Visual Studio Code as the main IDE  

---

## Setup Instructions

### 1. Clone the repository


---

## Setup Instructions

1. **Install Python 3.12 or newer**  
   Download from [python.org](https://www.python.org/downloads/).

2. **Install Flask**  
   Open a terminal in the project folder and run:
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**  
   In the terminal, run:
   ```
   python app.py
   ```
   The app will start at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

4. **First-Time Database Setup**  
   The database (`attendence.db`) is created automatically the first time you run the app.

# Frontend Setup (React + Vite)

### 1. Open a new terminal window (backend must keep running)

cd frontend

### 2. Install frontend dependencies

npm install


### 3. Start the development server

npm run dev











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


## New install

### Backend

#### 1. Clone the project

#### 2. Backend setup
cd attendence-tracker
```
python3 -m venv venv
```
source venv/bin/activate
```
pip install -r requirements.txt
```
python3 app.py
```

### Frontend

#### 1. New terminal while Flask still running 
cd frontend
```
npm install
```
npm run dev
```
