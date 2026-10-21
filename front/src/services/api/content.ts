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

/** One row of GET /contents/all/ (admins only): every post, any author, drafts included. */
export interface AdminContentRow {
  id: number;
  title: string;
  type: 'article' | 'podcast';
  format?: 'text' | 'audio' | 'video' | 'pdf' | null;
  status: 'draft' | 'published';
  is_premium: boolean;
  price?: number | null;
  author_name?: string | null;
  author?: { id: number; name: string | null } | null;
  updated_at: string;
}

export const getAllContentsForAdmin = async (params: { q?: string; status?: string; type?: string } = {}) =>
  (await apiClient.get<AdminContentRow[]>('/contents/all/', { params })).data;

/** Publish or move back to draft (admins: any post; authors: their own). */
export const updateContentStatus = async (contentId: number, status: AdminContentRow['status']) =>
  (await apiClient.patch<AdminContentRow>(`/contents/${contentId}`, { status })).data;
