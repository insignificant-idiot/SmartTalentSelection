import { create } from "zustand";
import api from "../services/api";

const useRankingStore = create((set) => ({
  ranking: null,
  loading: false,
  rankCandidates: async (jdText) => {
    set({ loading: true });
    try {
      const { data } = await api.post(`/rank?jd=${encodeURIComponent(jdText)}`);
      set({ ranking: data, loading: false });
      return data;
    } catch (error) {
      console.error("Ranking failed", error);
      set({ loading: false });
      throw error;
    }
  },
}));

export default useRankingStore;
