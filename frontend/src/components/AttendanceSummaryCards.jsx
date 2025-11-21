export function AttendanceSummaryCards({
  totalRecorded,
  presentCount,
  absentCount,
  attendancePercent,
  sessionsRecordedCourse,
  totalSessionsCourse,
}) {
  if (totalRecorded === 0) return null;

  return (
    <div className="grid sm:grid-cols-3 gap-4 text-sm">
      <div className="border rounded-lg p-3 bg-gray-50">
        <p className="text-gray-600">Sessions recorded</p>
        <p className="text-xl font-semibold">
          {sessionsRecordedCourse !== null && totalSessionsCourse !== null
            ? `${sessionsRecordedCourse} / ${totalSessionsCourse}`
            : totalRecorded}
        </p>
      </div>

      <div className="border rounded-lg p-3 bg-green-50">
        <p className="text-gray-600">Present</p>
        <p className="text-xl font-semibold text-green-700">
          {presentCount}
        </p>
      </div>

      <div className="border rounded-lg p-3 bg-red-50">
        <p className="text-gray-600">Absent</p>
        <p className="text-xl font-semibold text-red-700">
          {absentCount}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Attendance:{" "}
          <span className="font-medium">{attendancePercent}%</span>
        </p>
      </div>
    </div>
  );
}
