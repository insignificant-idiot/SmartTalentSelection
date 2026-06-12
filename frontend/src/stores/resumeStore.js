import { create } from "zustand";
import api from "../services/api";

const useResumeStore = create((set, get) => ({
  resumes: [],
  uploadLoading: false,
  fetchResumes: async () => {
    const { data } = await api.get("/upload/resumes");
    set({ resumes: data });
  },
  uploadResume: async (file, jobId) => {
    set({ uploadLoading: true });
    const formData = new FormData();
    formData.append("file", file);
    if (jobId) formData.append("job_id", jobId);
    try {
      const { data } = await api.post("/upload/resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await get().fetchResumes();
      return data;
    } finally {
      set({ uploadLoading: false });
    }
  },
}));

export default useResumeStore;
