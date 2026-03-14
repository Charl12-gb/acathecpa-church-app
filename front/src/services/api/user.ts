import apiClient from './index';
import { User, UserUpdatePayload } from '../../types/api'; // Adjust path if necessary

export const getUsers = async (
  role: string = '',
  skip: number = 0,
  limit: number = 100,
  filters: Record<string, any> = {}
): Promise<User[]> => {
  const params: Record<string, any> = {
    skip,
    limit,
    ...filters,
  };

  if (role) {
    params.role = role;
  }

  const response = await apiClient.get<User[]>('/users/', { params });
  return response.data;
};

export const getUserById = async (userId: number): Promise<User> => {
  const response = await apiClient.get<User>(`/users/${userId}`);
  return response.data;
};

export const updateUser = async (userId: number, userData: UserUpdatePayload): Promise<User> => {
  const response = await apiClient.put<User>(`/users/${userId}`, userData);
  return response.data;
};

export const deleteUser = async (userId: number): Promise<User> => {
  // The backend returns the deleted user object.
  // If it returned No Content (204), the Promise type would be void.
  const response = await apiClient.delete<User>(`/users/${userId}`);
  return response.data;
};
