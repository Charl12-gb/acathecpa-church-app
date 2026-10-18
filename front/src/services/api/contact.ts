import apiClient from './index';

export interface ContactPayload {
  name: string;
  email: string;
  subject: string;
  message: string;
  /** Honeypot: always empty for real visitors. */
  website?: string;
}

export const sendContactMessage = async (
  payload: ContactPayload,
): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>('/contact', payload);
  return response.data;
};
