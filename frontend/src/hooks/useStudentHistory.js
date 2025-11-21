import { useEffect, useState } from "react";
import { api } from "../api";

export function useStudentHistory(userId) {
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const { data } = await api.get(`/student/${userId}/attendance`);
      setHistory(data);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (!userId) return;
    loadHistory();
  }, [userId]);

  return { history, loadingHistory, reloadHistory: loadHistory };
}
