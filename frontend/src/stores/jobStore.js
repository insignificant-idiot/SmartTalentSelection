import { create } from "zustand";
import api from "../services/api";

const useJobStore = create((set, get) => ({
  jobs: [],
  loading: false,
  fetchJobs: async () => {
    set({ loading: true });
    try {
      const { data } = await api.get("/jobs");
      set({ jobs: data, loading: false });
    } catch (error) {
      console.error("Failed to fetch jobs", error);
      set({ loading: false });
    }
  },
  createJob: async (jobData) => {
    const { data } = await api.post("/jobs", jobData);
    await get().fetchJobs();
    return data;
  },
}));

export default useJobStore;
