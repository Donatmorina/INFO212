export function CourseTabs({ history, courses, selectedCourseId, onSelect }) {
  if (history.length === 0) {
    return (
      <p className="text-gray-500 text-sm">
        No attendance recorded yet.
      </p>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={() => onSelect("ALL")}
        className={
          "px-3 py-1 rounded-full text-sm border " +
          (selectedCourseId === "ALL"
            ? "bg-blue-600 text-white border-blue-600"
            : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50")
        }
      >
        All courses
      </button>

      {courses.map((c) => (
        <button
          key={c.id}
          type="button"
          onClick={() => onSelect(c.id)}
          className={
            "px-3 py-1 rounded-full text-sm border " +
            (selectedCourseId === c.id
              ? "bg-blue-600 text-white border-blue-600"
              : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50")
          }
        >
          {c.course_name} ({c.course_code})
        </button>
      ))}
    </div>
  );
}
