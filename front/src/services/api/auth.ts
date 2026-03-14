import apiClient from './index';
import { User, UserCreatePayload, TokenResponse, LoginPayload } from '../../types/api'; // Adjust path if necessary

export const register = async (userData: UserCreatePayload): Promise<User> => {
  const response = await apiClient.post<User>('/auth/register', userData);
  return response.data;
};

export const login = async (credentials: LoginPayload): Promise<TokenResponse> => {
  // FastAPI's OAuth2PasswordRequestForm expects form data
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await apiClient.post<TokenResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const refreshToken = async (currentToken: string): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/token/refresh', null, { // No body needed for this specific endpoint
     headers: {
         'Authorization': `Bearer ${currentToken}`
     }
  });
  return response.data;
};

export const getMe = async (): Promise<User> => {
  const response = await apiClient.get<User>('/auth/users/me');
  return response.data;
};

export const requestPasswordReset = async (email: string): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>('/auth/forgot-password', { email });
  return response.data; // Backend returns a message like {"message": "..."}
};

export const resetPassword = async (token: string, newPassword: string): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>('/auth/reset-password', {
    token: token,
    new_password: newPassword,
  });
  return response.data; // Backend returns a message like {"message": "..."}
};
