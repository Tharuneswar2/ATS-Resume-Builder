import axios from "axios";
import type { Profile, JDAnalysis, JDScore } from "../types";

const API_BASE_URL = "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const ProfileAPI = {
  list: async (skip = 0, limit = 10): Promise<Profile[]> => {
    const response = await apiClient.get(`/profiles/?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  get: async (id: string): Promise<Profile> => {
    const response = await apiClient.get(`/profiles/${id}`);
    return response.data;
  },
  create: async (profile: Profile): Promise<Profile> => {
    const response = await apiClient.post(`/profiles/`, profile);
    return response.data;
  },
  update: async (id: string, profileUpdate: Partial<Profile>): Promise<Profile> => {
    const response = await apiClient.patch(`/profiles/${id}`, profileUpdate);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/profiles/${id}`);
  },
};

export const ResumeAPI = {
  generateAndDownload: async (profileId: string, template: string = "00_ats_optimized.tex.j2") => {
    const response = await apiClient.post(`/resume/generate/${profileId}?template=${template}`, null, {
      responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `resume_${profileId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
  getAtsScore: async (profileId: string, template: string = "00_ats_optimized.tex.j2") => {
    const response = await apiClient.get(`/resume/ats-score/${profileId}?template=${template}`);
    return response.data;
  }
};

export const JdAPI = {
  analyze: async (text: string): Promise<JDAnalysis> => {
    const response = await apiClient.post(`/jd/analyze`, { text });
    return response.data;
  },
  scoreProfile: async (profileId: string, text: string): Promise<JDScore> => {
    const response = await apiClient.post(`/jd/score/${profileId}`, { text });
    return response.data;
  }
};
