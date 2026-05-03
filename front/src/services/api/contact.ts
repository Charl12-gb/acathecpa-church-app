import apiClient from './index';

export interface ContactPayload {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export const sendContactMessage = async (
  payload: ContactPayload,
): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>('/contact', payload);
  return response.data;
};
