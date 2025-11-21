export function AttendanceHistoryList({ loading, history }) {
  if (loading) {
    return <p>Loading…</p>;
  }

  if (history.length === 0) {
    return (
      <p className="text-gray-500 text-sm">
        No attendance records yet for this selection.
      </p>
    );
  }

  return (
    <ul className="divide-y">
      {history.map((row, idx) => (
        <li
          key={idx}
          className="py-3 flex items-center justify-between gap-4"
        >
          <div>
            <div className="font-medium">
              {row.course_name}{" "}
              <span className="text-gray-500 text-sm">
                ({row.course_code})
              </span>
            </div>
            <div className="text-sm text-gray-600">{row.date}</div>
          </div>
          <span
            className={
              "px-2 py-1 rounded text-sm " +
              (row.status === "Present"
                ? "bg-green-100 text-green-700"
                : row.status === "Excused"
                ? "bg-yellow-100 text-yellow-700"
                : "bg-red-100 text-red-700")
            }
          >
            {row.status}
          </span>
        </li>
      ))}
    </ul>
  );
}
