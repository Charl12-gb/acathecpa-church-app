import apiClient from './index';
import { Content, ContentCreatePayload, ContentUpdatePayload, ContentType, ContentStatus } from '../../types/api'; // Adjust path

export const getAllContents = async (params?: { skip?: number; limit?: number; type?: ContentType; status?: ContentStatus }): Promise<Content[]> => {
  const response = await apiClient.get<Content[]>('/contents/', { params });
  return response.data;
};

export const getUserContents = async (params?: { skip?: number; limit?: number; status?: ContentStatus }): Promise<Content[]> => {
  // Backend router for this specific "user's own content" might be different, e.g. /contents/me
  // The current backend router for /contents/user expects current_user from token.
  const response = await apiClient.get<Content[]>('/contents/user', { params });
  return response.data;
};

export const getContentById = async (contentId: number): Promise<Content> => {
  const response = await apiClient.get<Content>(`/contents/${contentId}`);
  return response.data;
};

export const createContent = async (data: ContentCreatePayload): Promise<Content> => {
  const response = await apiClient.post<Content>('/contents/', data);
  return response.data;
};

export const updateContent = async (contentId: number, data: ContentUpdatePayload): Promise<Content> => {
  const response = await apiClient.put<Content>(`/contents/${contentId}`, data);
  return response.data;
};

export const deleteContent = async (contentId: number): Promise<Content> => {
  // Backend returns the deleted content object
  const response = await apiClient.delete<Content>(`/contents/${contentId}`);
  return response.data;
};

export const publishContent = async (contentId: number): Promise<Content> => {
  const response = await apiClient.post<Content>(`/contents/${contentId}/publish`); // No body needed, just the action
  return response.data;
};
