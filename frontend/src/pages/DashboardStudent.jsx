import { useState, useMemo } from "react";
import { useStudentHistory } from "../hooks/useStudentHistory";
import { useCourseSummary } from "../hooks/useCourseSummary";
import { CourseTabs } from "../components/CourseTabs";
import { AttendanceSummaryCards } from "../components/AttendanceSummaryCards";
import { AttendanceHistoryList } from "../components/AttendanceHistoryList";

export default function DashboardStudent({ user, onLogout }) {
  const [selectedCourseId, setSelectedCourseId] = useState("ALL");

  const { history, loadingHistory } = useStudentHistory(user.id);
  const { courseSummary, loadingSummary } = useCourseSummary(selectedCourseId);

  const courses = useMemo(
    () =>
      Array.from(
        new Map(
          history.map((row) => [
            row.course_id,
            {
              id: row.course_id,
              course_name: row.course_name,
              course_code: row.course_code,
            },
          ])
        ).values()
      ),
    [history]
  );

  const filteredHistory =
    selectedCourseId === "ALL"
      ? history
      : history.filter((row) => row.course_id === selectedCourseId);

  const totalRecorded = filteredHistory.length;
  const presentCount = filteredHistory.filter(
    (r) => r.status === "Present"
  ).length;
  const absentCount = filteredHistory.filter(
    (r) => r.status === "Absent"
  ).length;
  const attendancePercent =
    totalRecorded > 0 ? Math.round((presentCount / totalRecorded) * 100) : 0;

  const selectedCourse =
    selectedCourseId === "ALL"
      ? null
      : courses.find((c) => c.id === selectedCourseId);

  const sessionsRecordedCourse =
    selectedCourseId !== "ALL" && courseSummary
      ? courseSummary.sessions_recorded
      : null;

  const totalSessionsCourse =
    selectedCourseId !== "ALL" && courseSummary
      ? courseSummary.total_sessions
      : null;

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* HEADER */}
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Student Dashboard</h1>
          <p className="text-sm text-gray-600">
            Logged in as student 
          </p>
        </div>
        <button
          onClick={onLogout}
          className="self-start md:self-auto bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700"
        >
          Logout
        </button>
      </header>

      {/* COURSE TABS */}
      <section className="bg-white p-4 rounded-xl shadow">
        <h2 className="font-semibold mb-2 text-sm text-gray-700">
          Your courses
        </h2>
        <CourseTabs
          history={history}
          courses={courses}
          selectedCourseId={selectedCourseId}
          onSelect={setSelectedCourseId}
        />
      </section>

      {/* SUMMARY + HISTORY */}
      <section className="bg-white p-5 rounded-xl shadow space-y-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <h2 className="font-semibold text-lg">Attendance overview</h2>
          <p className="text-sm text-gray-600">
            Showing:{" "}
            <span className="font-medium">
              {selectedCourse
                ? `${selectedCourse.course_name} (${selectedCourse.course_code})`
                : "All courses"}
            </span>
          </p>
        </div>

        <AttendanceSummaryCards
          totalRecorded={totalRecorded}
          presentCount={presentCount}
          absentCount={absentCount}
          attendancePercent={attendancePercent}
          sessionsRecordedCourse={sessionsRecordedCourse}
          totalSessionsCourse={totalSessionsCourse}
        />

        {selectedCourseId !== "ALL" && (
          <div className="mt-1">
            {loadingSummary ? (
              <p className="text-sm text-gray-500">Loading course info…</p>
            ) : courseSummary ? (
              <p className="text-sm text-gray-700">
                To meet the attendance requirement for this course you must
                attend{" "}
                <span className="font-medium">
                  {courseSummary.compulsory_sessions}
                </span>{" "}
                of{" "}
                <span className="font-medium">
                  {courseSummary.total_sessions}
                </span>{" "}
                sessions. You can be absent up to{" "}
                <span className="font-medium">
                  {courseSummary.allowed_skips}
                </span>{" "}
                times.
              </p>
            ) : (
              <p className="text-sm text-gray-500">
                No course requirement information available.
              </p>
            )}
          </div>
        )}

        <div className="mt-4">
          <h3 className="font-semibold mb-2">Attendance history</h3>
          <AttendanceHistoryList
            loading={loadingHistory}
            history={filteredHistory}
          />
        </div>
      </section>
    </div>
  );
}
