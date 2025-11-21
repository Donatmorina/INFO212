import { useEffect, useState } from "react";
import { api } from "../api";

export function CourseAttendanceHistory({ courseId, courses }) {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!courseId) {
        setRecords([]);
        return;
      }
      const { data } = await api.get(`/course/${courseId}/attendance`);
      setRecords(data);
    };
    fetchHistory();
  }, [courseId]);

  if (!courseId) {
    return (
      <p className="text-gray-500 text-sm">
        Select a course to view its attendance history.
      </p>
    );
  }

  if (!records.length) {
    return (
      <p className="text-gray-500 text-sm">
        No attendance records yet for this course.
      </p>
    );
  }

  const grouped = records.reduce((acc, rec) => {
    if (!acc[rec.date]) acc[rec.date] = [];
    acc[rec.date].push(rec);
    return acc;
  }, {});

  const courseName =
    courses.find((c) => c.id === Number(courseId))?.course_name || "Course";

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-700 mb-2">
        Showing attendance history for <b>{courseName}</b>
      </p>

      {Object.entries(grouped).map(([date, list]) => (
        <div key={date} className="border border-gray-200 rounded-lg">
          <div className="bg-gray-100 px-4 py-2 font-medium text-sm">
            Date: {date}
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="p-2 text-left">Student</th>
                <th className="p-2 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {list.map((rec, idx) => (
                <tr key={idx} className="border-t">
                  <td className="p-2">{rec.student_name}</td>
                  <td className="p-2">
                    <span
                      className={
                        rec.status === "Present"
                          ? "text-green-600 font-medium"
                          : "text-red-600 font-medium"
                      }
                    >
                      {rec.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
