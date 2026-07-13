import apiClient from './index';
import type { Category, CategoryPayload } from '../../types/api';

export const getCategories = async (): Promise<Category[]> => {
  const response = await apiClient.get<Category[]>('/categories/');
  return response.data;
};

export const createCategory = async (data: CategoryPayload): Promise<Category> => {
  const response = await apiClient.post<Category>('/categories/', data);
  return response.data;
};

export const updateCategory = async (id: number, data: Partial<CategoryPayload>): Promise<Category> => {
  const response = await apiClient.put<Category>(`/categories/${id}`, data);
  return response.data;
};

export const deleteCategory = async (id: number): Promise<void> => {
  await apiClient.delete(`/categories/${id}`);
};
