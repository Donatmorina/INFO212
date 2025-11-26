import { useEffect, useState } from "react";
import { api } from "../api";
import { AttendanceForm } from "../components/AttendanceForm";
import { CourseAttendanceHistory } from "../components/CourseAttendanceHistory";
import { CourseSummary } from "../components/CourseSummary";

export default function DashboardTA({ user, onLogout }) {
  const [courses, setCourses] = useState([]);
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState({
    course_name: "",
    course_code: "",
    total_sessions: 0,
    required_percent: 0,
  });
  const [enroll, setEnroll] = useState({ student_id: "", course_id: "" });
  const [msg, setMsg] = useState("");
  const [selectedCourseId, setSelectedCourseId] = useState("");

  const loadCourses = async () => {
    const { data } = await api.get("/courses");
    setCourses(data);
  };

  const loadStudents = async () => {
    const { data } = await api.get("/students");
    setStudents(data);
  };

  useEffect(() => {
    loadCourses();
    loadStudents();
  }, []);

  const addCourse = async (e) => {
    e.preventDefault();
    setMsg("");

    const total = Number(form.total_sessions) || 0;
    let percent = Number(form.required_percent) || 0;
    if (percent < 0) percent = 0;
    if (percent > 100) percent = 100;

    const compulsory = Math.round((total * percent) / 100);

    await api.post("/courses", {
      course_name: form.course_name.trim(),
      course_code: form.course_code.trim(),
      total_sessions: total,
      compulsory_sessions: compulsory,
    });

    setForm({
      course_name: "",
      course_code: "",
      total_sessions: 0,
      required_percent: 0,
    });
    setMsg("Course added ✅");
    loadCourses();
  };

  const enrollStudent = async (e) => {
    e.preventDefault();
    if (!enroll.student_id || !enroll.course_id) return;
    await api.post("/enroll", enroll);
    setMsg("Student enrolled ✅");
    setEnroll({ student_id: "", course_id: "" });
  };

  const handleCourseCardClick = (id) => {
    const idString = String(id);
    setSelectedCourseId(idString);
    const el = document.getElementById("mark-attendance-section");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/*  HEADER  */}
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <h1 className="text-2xl font-semibold">Teaching Assistant Dashboard</h1>
        <div className="flex items-center gap-4">
          <p className="text-sm text-gray-600">
            Logged in as: <span className="font-medium">{user.role}</span> 
          </p>
          <button
            onClick={onLogout}
            className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700"
          >
            Logout
          </button>
        </div>
      </header>

      {msg && <p className="text-green-600 font-medium">{msg}</p>}

      {/* GRID: ADD COURSE + ENROLL STUDENTS */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* ADD COURSE */}
        <section className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-lg font-semibold mb-4">➕ Add New Course</h2>
          <form onSubmit={addCourse} className="space-y-3">
            <input
              placeholder="Course Name"
              className="w-full border p-2 rounded"
              value={form.course_name}
              onChange={(e) =>
                setForm({ ...form, course_name: e.target.value })
              }
            />
            <input
              placeholder="Course Code"
              className="w-full border p-2 rounded"
              value={form.course_code}
              onChange={(e) =>
                setForm({ ...form, course_code: e.target.value })
              }
            />

            <div className="grid grid-cols-3 gap-3">
              <p className="col-span-3 text-sm text-gray-600">
                Total sessions:
              </p>
              <input
                type="number"
                placeholder="Total Sessions"
                className="w-full border p-2 rounded"
                value={form.total_sessions}
                onChange={(e) =>
                  setForm({ ...form, total_sessions: e.target.value })
                }
              />

              <p className="col-span-3 text-sm text-gray-600">
                Required %:
              </p>
              <input
                type="number"
                placeholder="Required %"
                className="w-full border p-2 rounded"
                value={form.required_percent}
                onChange={(e) =>
                  setForm({ ...form, required_percent: e.target.value })
                }
              />

              <div className="flex items-center text-xs md:text-sm text-gray-600">
                {(() => {
                  const total = Number(form.total_sessions) || 0;
                  const pct = Math.min(
                    100,
                    Math.max(0, Number(form.required_percent) || 0)
                  );
                  const comp = Math.round((total * pct) / 100);
                  return (
                    <span>
                      Compulsory ≈ <b>{comp}</b>
                    </span>
                  );
                })()}
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Add Course
            </button>
          </form>
        </section>

        {/* ENROLL STUDENT */}
        <section className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-lg font-semibold mb-4">🎓 Enroll Student</h2>
          <form onSubmit={enrollStudent} className="space-y-3">
            <select
              className="w-full border p-2 rounded"
              value={enroll.student_id}
              onChange={(e) =>
                setEnroll({ ...enroll, student_id: e.target.value })
              }
            >
              <option value="">Select Student</option>
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>

            <select
              className="w-full border p-2 rounded"
              value={enroll.course_id}
              onChange={(e) =>
                setEnroll({ ...enroll, course_id: e.target.value })
              }
            >
              <option value="">Select Course</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.course_name} ({c.course_code})
                </option>
              ))}
            </select>

            <button
              type="submit"
              className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Enroll
            </button>
          </form>
        </section>
      </div>

      {/* COURSE OVERVIEW */}
      <section className="bg-white p-6 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-4">📘 Course Overview</h2>

        {courses.length === 0 ? (
          <p className="text-gray-500">No courses added yet.</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {courses.map((c) => {
              const pct =
                c.total_sessions > 0
                  ? Math.round(
                      (100 * (c.compulsory_sessions || 0)) / c.total_sessions
                    )
                  : 0;
              const isActive = String(c.id) === selectedCourseId;

              return (
                <button
                  type="button"
                  key={c.id}
                  onClick={() => handleCourseCardClick(c.id)}
                  className={
                    "text-left border p-4 rounded-lg hover:shadow transition " +
                    (isActive
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 bg-white")
                  }
                >
                  <h3 className="font-semibold text-lg text-blue-700">
                    {c.course_name}{" "}
                    <span className="text-gray-500">({c.course_code})</span>
                  </h3>
                  <div className="text-sm text-gray-700 mt-1 space-y-1">
                    <p>
                      Total sessions: <b>{c.total_sessions}</b>
                    </p>
                    <p>
                      Compulsory: <b>{c.compulsory_sessions}</b>
                    </p>
                    <p>
                      Required attendance: <b>{pct}%</b>
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </section>

      {/* MARK ATTENDANCE */}
      <section
        id="mark-attendance-section"
        className="bg-white p-6 rounded-xl shadow"
      >
        <h2 className="text-lg font-semibold mb-4">📅 Mark Attendance</h2>
        <AttendanceForm
          courses={courses}
          selectedCourse={selectedCourseId}
          setSelectedCourse={setSelectedCourseId}
        />
      </section>

      {/* COURSE ATTENDANCE HISTORY + SUMMARY */}
      <section className="bg-white p-6 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-4">📊 Attendance History</h2>

        <CourseSummary courseId={selectedCourseId} />
        <CourseAttendanceHistory courseId={selectedCourseId} courses={courses} />
      </section>
    </div>
  );
}
