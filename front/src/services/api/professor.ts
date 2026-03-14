import apiClient from './index';
import { 
    Professor,
    ProfessorProfile,
    ProfessorProfileCreatePayload,
    ProfessorProfileUpdatePayload,
} from '../../types/api';

import { getUserById, getUsers as getAllUsers } from './user';

export interface ProfessorUserAndProfileCreatePayload {
    name?: string;
    email: string;
    password?: string;
    phone?: string | null;
    country?: string | null;
    birthdate?: string | null;
    specialization: string;
    bio?: string | null;
    education?: any[];
    experience?: any[];
    skills?: string[];
    social_links?: any;
}

export async function getProfessor(userId: number): Promise<Professor> {
    const user = await getUserById(userId);
    return user as Professor;
}

export async function createProfessorUserAndProfile(payload: ProfessorUserAndProfileCreatePayload): Promise<Professor> {
    const response = await apiClient.post<Professor>(`/professors/`, payload);
    return response.data;
}

export async function createProfessorProfile(userId: number, profileData: ProfessorProfileCreatePayload): Promise<ProfessorProfile> {
    const response = await apiClient.post<ProfessorProfile>(`professors/${userId}/profile`, profileData);
    return response.data;
}

export async function updateProfessorProfile(userId: number, profileData: ProfessorProfileUpdatePayload): Promise<ProfessorProfile> {
    const response = await apiClient.put<ProfessorProfile>(`professors/${userId}/profile`, profileData);
    return response.data;
}

export async function deleteProfessorProfile(userId: number): Promise<void> {
    await apiClient.delete(`professors/${userId}/profile`);
}

export async function getProfessors(params: { skip?: number; limit?: number; [key: string]: any } = {}): Promise<Professor[]> {
  const { skip = 0, limit = 100, ...rest } = params;
  const users = await getAllUsers('professor', skip, limit, rest);
  return users as Professor[];
}
