import { useEffect, useState } from "react";
import { api } from "../api";

export function CourseSummary({ courseId }) {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      if (!courseId) {
        setSummary(null);
        return;
      }
      try {
        const { data } = await api.get(`/course/${courseId}/summary`);
        setSummary(data);
      } catch (err) {
        console.error("Failed to load course summary", err);
      }
    };
    fetchSummary();
  }, [courseId]);

  if (!courseId || !summary) return null;

  if (!summary.students.length) {
    return (
      <p className="text-gray-500 text-sm mb-4">
        No attendance data yet for this course.
      </p>
    );
  }

  return (
    <div className="mb-6">
      <h3 className="font-semibold text-sm mb-2">
        Course summary — Sessions recorded: {summary.sessions_recorded} /{" "}
        {summary.total_sessions}
      </h3>

      <table className="w-full text-sm border">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Student</th>
            <th className="p-2 text-center">Present</th>
            <th className="p-2 text-center">Absent</th>
            <th className="p-2 text-center">% attended</th>
            <th className="p-2 text-center">Skips left</th>
          </tr>
        </thead>
        <tbody>
          {summary.students.map((s) => (
            <tr key={s.student_id} className="border-t">
              <td className="p-2">{s.name}</td>
              <td className="p-2 text-center">{s.present}</td>
              <td className="p-2 text-center">{s.absent}</td>
              <td className="p-2 text-center">{s.attendance_percent}%</td>
              <td className="p-2 text-center">{s.remaining_skips}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
