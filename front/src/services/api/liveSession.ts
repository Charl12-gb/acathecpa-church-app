import apiClient from './index';
import {
  JitsiJoinResponse,
  LiveSession,
  LiveSessionAttendanceSummary,
  LiveSessionCreatePayload,
  LiveSessionReschedulePayload,
  LiveSessionUpdatePayload,
} from '../../types/api';

export const createLiveSession = async (data: LiveSessionCreatePayload): Promise<LiveSession> => {
  const response = await apiClient.post<LiveSession>('/live-sessions/', data);
  return response.data;
};

export const getAllLiveSessions = async (params?: { skip?: number; limit?: number }): Promise<LiveSession[]> => {
  const response = await apiClient.get<LiveSession[]>('/live-sessions/', { params });
  return response.data;
};

export const getLiveSessionsForCourse = async (courseId: number, params?: { skip?: number; limit?: number }): Promise<LiveSession[]> => {
  const response = await apiClient.get<LiveSession[]>(`/live-sessions/course/${courseId}`, { params });
  return response.data;
};

export const getLiveSessionById = async (sessionId: number): Promise<LiveSession> => {
  const response = await apiClient.get<LiveSession>(`/live-sessions/${sessionId}`);
  return response.data;
};

export const getLiveSessionAttendance = async (sessionId: number): Promise<LiveSessionAttendanceSummary> => {
  const response = await apiClient.get<LiveSessionAttendanceSummary>(`/live-sessions/${sessionId}/attendance`);
  return response.data;
};

export const updateLiveSession = async (sessionId: number, data: LiveSessionUpdatePayload): Promise<LiveSession> => {
  const response = await apiClient.put<LiveSession>(`/live-sessions/${sessionId}`, data);
  return response.data;
};

export const updateLiveSessionStatus = async (sessionId: number, status: string): Promise<LiveSession> => {
  const response = await apiClient.patch<LiveSession>(`/live-sessions/${sessionId}/status`, { status });
  return response.data;
};

export const rescheduleLiveSession = async (sessionId: number, data: LiveSessionReschedulePayload): Promise<LiveSession> => {
  const response = await apiClient.post<LiveSession>(`/live-sessions/${sessionId}/reschedule`, data);
  return response.data;
};

export const deleteLiveSession = async (sessionId: number): Promise<any> => {
  const response = await apiClient.delete(`/live-sessions/${sessionId}`);
  return response.data;
};

export const joinLiveSession = async (sessionId: number): Promise<JitsiJoinResponse> => {
  const response = await apiClient.post<JitsiJoinResponse>(`/live-sessions/${sessionId}/join`);
  return response.data;
};

export const leaveLiveSession = async (sessionId: number): Promise<void> => {
  await apiClient.post(`/live-sessions/${sessionId}/leave`);
};
