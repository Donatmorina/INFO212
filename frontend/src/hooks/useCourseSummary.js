import { useEffect, useState } from "react";
import { api } from "../api";

export function useCourseSummary(selectedCourseId) {
  const [courseSummary, setCourseSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    const fetchSummary = async () => {
      if (selectedCourseId === "ALL" || !selectedCourseId) {
        setCourseSummary(null);
        return;
      }
      setLoadingSummary(true);
      try {
        const { data } = await api.get(`/course/${selectedCourseId}/summary`);
        setCourseSummary(data);
      } catch (err) {
        console.error("Failed to load course summary", err);
        setCourseSummary(null);
      } finally {
        setLoadingSummary(false);
      }
    };

    fetchSummary();
  }, [selectedCourseId]);

  return { courseSummary, loadingSummary };
}
