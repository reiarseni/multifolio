import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface WorkExperience {
  id: string;
  profile_id: string;
  company: string;
  position: string;
  description: string | null;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  location: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Education {
  id: string;
  profile_id: string;
  institution: string;
  degree: string;
  field: string | null;
  description: string | null;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: string;
  profile_id: string;
  name: string;
  category: string | null;
  level: string | null;
  is_transversal: boolean;
  sort_order: number;
  created_at: string;
}

export interface Certification {
  id: string;
  profile_id: string;
  name: string;
  issuer: string;
  issue_date: string | null;
  expiry_date: string | null;
  credential_url: string | null;
  sort_order: number;
  created_at: string;
}

export interface BaseProfile {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  phone: string | null;
  location: string | null;
  title: string | null;
  bio: string | null;
  photo_url: string | null;
  website: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  created_at: string;
  updated_at: string;
  experiences: WorkExperience[];
  educations: Education[];
  skills: Skill[];
  certifications: Certification[];
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const profileApi = {
  get: () => apiClient.get<BaseProfile>("/api/profile", withAuth()),

  update: (data: Partial<BaseProfile>) =>
    apiClient.put<BaseProfile>("/api/profile", data, withAuth()),

  createExperience: (data: Partial<WorkExperience>) =>
    apiClient.post<WorkExperience>("/api/profile/experiences", data, withAuth()),

  updateExperience: (id: string, data: Partial<WorkExperience>) =>
    apiClient.put<WorkExperience>(`/api/profile/experiences/${id}`, data, withAuth()),

  deleteExperience: (id: string) =>
    apiClient.delete(`/api/profile/experiences/${id}`, withAuth()),

  createEducation: (data: Partial<Education>) =>
    apiClient.post<Education>("/api/profile/education", data, withAuth()),

  updateEducation: (id: string, data: Partial<Education>) =>
    apiClient.put<Education>(`/api/profile/education/${id}`, data, withAuth()),

  deleteEducation: (id: string) =>
    apiClient.delete(`/api/profile/education/${id}`, withAuth()),

  createSkill: (data: Partial<Skill>) =>
    apiClient.post<Skill>("/api/profile/skills", data, withAuth()),

  updateSkill: (id: string, data: Partial<Skill>) =>
    apiClient.put<Skill>(`/api/profile/skills/${id}`, data, withAuth()),

  deleteSkill: (id: string) =>
    apiClient.delete(`/api/profile/skills/${id}`, withAuth()),

  createCertification: (data: Partial<Certification>) =>
    apiClient.post<Certification>("/api/profile/certifications", data, withAuth()),

  updateCertification: (id: string, data: Partial<Certification>) =>
    apiClient.put<Certification>(`/api/profile/certifications/${id}`, data, withAuth()),

  deleteCertification: (id: string) =>
    apiClient.delete(`/api/profile/certifications/${id}`, withAuth()),
};
