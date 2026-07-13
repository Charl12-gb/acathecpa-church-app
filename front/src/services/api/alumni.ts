import apiClient from './index';
import type { Alumnus } from '../../types/api';

export const getAlumni = async (): Promise<Alumnus[]> => {
  const response = await apiClient.get<Alumnus[]>('/alumni');
  return response.data;
};
