import { User } from './userTypes'; // Assuming User type is already defined

export enum ContentType {
  ARTICLE = 'article',
  PODCAST = 'podcast',
}

export enum ContentFormat {
  AUDIO = 'audio',
  VIDEO = 'video',
  TEXT = 'text',
  PDF = 'pdf',
}

export enum ContentStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
}

export interface Content {
  id: number;
  title: string;
  description?: string | null;
  content_body?: string | null; // Matches SQLAlchemy model
  type: ContentType;
  format?: ContentFormat | null;
  media_url?: string | null;
  is_premium: boolean;
  price?: number | null;
  author_id: number;
  author?: User | null; // Populated by backend
  status: ContentStatus;
  tags?: string[] | null;
  created_at: string; // Or Date
  updated_at: string; // Or Date
}

export interface ContentCreatePayload {
  title: string;
  description?: string;
  content_body?: string;
  type: ContentType;
  format?: ContentFormat;
  media_url?: string;
  is_premium?: boolean;
  price?: number;
  tags?: string[];
  // author_id is set by backend from current_user
  status?: ContentStatus; // Optional, backend might default to draft
}

export interface ContentUpdatePayload {
  title?: string;
  description?: string;
  content_body?: string;
  type?: ContentType;
  format?: ContentFormat;
  media_url?: string;
  is_premium?: boolean;
  price?: number;
  status?: ContentStatus;
  tags?: string[];
}
