import apiClient from './index';
import { LiveSession, LiveSessionCreatePayload, LiveSessionUpdatePayload, AgoraTokenResponse } from '../../types/api'; // Adjust path

export const createLiveSession = async (data: LiveSessionCreatePayload): Promise<LiveSession> => {
  const response = await apiClient.post<LiveSession>('/live-sessions/', data);
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

export const updateLiveSession = async (sessionId: number, data: LiveSessionUpdatePayload): Promise<LiveSession> => {
  const response = await apiClient.put<LiveSession>(`/live-sessions/${sessionId}`, data);
  return response.data;
};

export const deleteLiveSession = async (sessionId: number): Promise<any> => { // Backend might return deleted session or just 204/200
  const response = await apiClient.delete(`/live-sessions/${sessionId}`);
  return response.data; // If 204, response.data might be undefined/null
};

// Example for joining a session and getting an Agora token (if backend handles this)
// The backend router for /live-sessions/{session_id}/join was not explicitly defined.
// This is a placeholder assuming such an endpoint might exist or be added.
export const joinLiveSession = async (sessionId: number, userId: number, isHost: boolean): Promise<AgoraTokenResponse> => {
  const response = await apiClient.post<AgoraTokenResponse>(`/live-sessions/${sessionId}/join`, { userId, isHost });
  return response.data;
};

// Example for actions within a live session (if backend proxies these)
// Backend routers for these were not detailed. Assuming simple POSTs for now.
// These are placeholders based on potential frontend store actions.
export const toggleParticipantAudio = async (sessionId: number, participantUserId: string, muted: boolean): Promise<void> => {
  // Example endpoint: /live-sessions/{sessionId}/participants/{participantUserId}/audio
  // This specific endpoint is not defined in the current backend plan.
  await apiClient.post(`/live-sessions/${sessionId}/participants/${participantUserId}/audio`, { muted });
};

export const toggleRaiseHand = async (sessionId: number, participantUserId: string, raised: boolean): Promise<void> => {
  // Example endpoint: /live-sessions/{sessionId}/participants/{participantUserId}/hand
  // This specific endpoint is not defined in the current backend plan.
  await apiClient.post(`/live-sessions/${sessionId}/participants/${participantUserId}/hand`, { raised });
};
