import apiClient from './index';
import { API_URL } from './Env';

export interface UploadResult {
  url: string;             // chemin relatif retourné par l'API (ex: /media/uploads/image/xxx.png)
  filename: string;
  original_name: string;
  size: number;
  content_type: string;
  category: 'image' | 'video' | 'audio' | 'document' | 'other';
}

export type UploadCategory = UploadResult['category'];

/**
 * Upload un fichier vers le backend Django.
 * Retourne l'objet UploadResult dont `url` est le chemin relatif (`/media/...`).
 *
 * @param file       Fichier sélectionné par l'utilisateur
 * @param category   Optionnel : force la catégorie côté serveur (image/video/audio/document)
 * @param onProgress Optionnel : callback de progression (0-100)
 */
export const uploadFile = async (
  file: File,
  category?: UploadCategory,
  onProgress?: (percent: number) => void
): Promise<UploadResult> => {
  const formData = new FormData();
  formData.append('file', file);
  if (category) formData.append('category', category);

  const response = await apiClient.post<UploadResult>('/uploads/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (evt) => {
      if (onProgress && evt.total) {
        onProgress(Math.round((evt.loaded * 100) / evt.total));
      }
    },
  });
  return response.data;
};

/**
 * Convertit une URL relative renvoyée par l'API (`/media/...`) en URL absolue
 * exploitable par <img>, <audio>, <video>, etc.
 * Les URLs déjà absolues (http(s)://) sont retournées telles quelles.
 */
export const resolveMediaUrl = (url: string | null | undefined): string => {
  if (!url) return '';
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith('/')) return `${API_URL}${url}`;
  return `${API_URL}/${url}`;
};
