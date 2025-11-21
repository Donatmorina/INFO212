import { useEffect, useState } from "react";
import { api } from "../api";

export function AttendanceForm({
  courses,
  selectedCourse,
  setSelectedCourse,
}) {
  const [students, setStudents] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [attendance, setAttendance] = useState({});
  const [feedback, setFeedback] = useState({});
  const [saveMessage, setSaveMessage] = useState("");

  useEffect(() => {
    const fetchStudents = async () => {
      if (!selectedCourse) {
        setStudents([]);
        setAttendance({});
        setFeedback({});
        setSelectedDate("");
        setSaveMessage("");
        return;
      }
      const { data } = await api.get(`/course/${selectedCourse}/students`);
      setStudents(data);
      const empty = {};
      data.forEach((s) => (empty[s.id] = "Absent"));
      setAttendance(empty);
      setFeedback({});
      setSelectedDate("");
      setSaveMessage("");
    };
    fetchStudents();
  }, [selectedCourse]);

  useEffect(() => {
    if (!students.length || !selectedDate) return;
    const resetAttendance = {};
    students.forEach((s) => (resetAttendance[s.id] = "Absent"));
    setAttendance(resetAttendance);
    setFeedback({});
    setSaveMessage("");
  }, [selectedDate, students]);

  const handleAttendanceChange = (id, status) => {
    setAttendance({ ...attendance, [id]: status });
  };

  const submitAttendance = async (e) => {
    e.preventDefault();
    if (!selectedCourse || !selectedDate) return;

    for (const [studentId, status] of Object.entries(attendance)) {
      await api.post("/attendance", {
        student_id: studentId,
        course_id: selectedCourse,
        date: selectedDate,
        status,
      });
    }

    const fb = {};
    Object.keys(attendance).forEach((sid) => {
      fb[sid] = "Saved";
    });
    setFeedback(fb);
    setSaveMessage(`Attendance saved for ${selectedDate}`);
  };

  return (
    <form onSubmit={submitAttendance} className="space-y-4">
      <div className="grid md:grid-cols-3 gap-4">
        <select
          className="border p-2 rounded"
          value={selectedCourse}
          onChange={(e) => setSelectedCourse(e.target.value)}
        >
          <option value="">Select Course</option>
          {courses.map((c) => (
            <option key={c.id} value={c.id}>
              {c.course_name} ({c.course_code})
            </option>
          ))}
        </select>

        <input
          type="date"
          className="border p-2 rounded"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          disabled={!selectedCourse}
        />

        <button
          type="submit"
          disabled={!selectedCourse || !selectedDate || students.length === 0}
          className={`px-4 py-2 rounded text-white ${
            !selectedCourse || !selectedDate || students.length === 0
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          Submit Attendance
        </button>
      </div>

      {saveMessage && (
        <p className="text-sm text-green-600 font-medium">{saveMessage}</p>
      )}

      {selectedCourse && students.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold mb-2">
            Students in{" "}
            {courses.find((c) => c.id === Number(selectedCourse))?.course_name ||
              "Course"}
          </h3>
          <table className="w-full border text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 text-left">Name</th>
                <th className="p-2 text-center">Present</th>
                <th className="p-2 text-center">Absent</th>
                <th className="p-2 text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.id} className="border-t">
                  <td className="p-2">{s.name}</td>
                  <td className="text-center">
                    <input
                      type="radio"
                      name={`status_${s.id}`}
                      checked={attendance[s.id] === "Present"}
                      onChange={() =>
                        handleAttendanceChange(s.id, "Present")
                      }
                    />
                  </td>
                  <td className="text-center">
                    <input
                      type="radio"
                      name={`status_${s.id}`}
                      checked={attendance[s.id] === "Absent"}
                      onChange={() =>
                        handleAttendanceChange(s.id, "Absent")
                      }
                    />
                  </td>
                  <td className="text-center">
                    {feedback[s.id] ? (
                      <span className="text-green-600 font-medium">
                        {feedback[s.id]}
                      </span>
                    ) : (
                      "-"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </form>
  );
}
