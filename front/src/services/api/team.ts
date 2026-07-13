import apiClient from './index';
import type { TeamMember, TeamMemberPayload } from '../../types/api';

export const getTeamMembers = async (): Promise<TeamMember[]> => {
  const response = await apiClient.get<TeamMember[]>('/team/');
  return response.data;
};

export const getTeamMember = async (id: number): Promise<TeamMember> => {
  const response = await apiClient.get<TeamMember>(`/team/${id}`);
  return response.data;
};

export const createTeamMember = async (data: TeamMemberPayload): Promise<TeamMember> => {
  const response = await apiClient.post<TeamMember>('/team/', data);
  return response.data;
};

export const updateTeamMember = async (id: number, data: Partial<TeamMemberPayload>): Promise<TeamMember> => {
  const response = await apiClient.put<TeamMember>(`/team/${id}`, data);
  return response.data;
};

export const deleteTeamMember = async (id: number): Promise<void> => {
  await apiClient.delete(`/team/${id}`);
};
