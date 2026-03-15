import { User } from './userTypes';

export enum LiveSessionStatus {
  SCHEDULED = 'scheduled',
  LIVE = 'live',
  ENDED = 'ended',
}

export interface LiveSession {
  id: number;
  course_id?: number | null;
  title: string;
  description?: string | null;
  scheduled_for: string; // Or Date
  duration_minutes?: number | null;
  host_id: number;
  host?: User | null;
  status: LiveSessionStatus;
  agora_channel_name?: string | null;
  // participants: User[]; // If backend sends participant list
}

export interface LiveSessionCreatePayload {
  course_id?: number | null;
  title: string;
  description?: string;
  scheduled_for: string; // ISO string
  duration_minutes?: number;
  // host_id is set by backend
  agora_channel_name?: string; // Optional, backend can generate
}

export interface LiveSessionUpdatePayload {
  title?: string;
  description?: string;
  scheduled_for?: string;
  duration_minutes?: number;
  status?: LiveSessionStatus;
  agora_channel_name?: string;
}

// For Agora token if backend provides it for joining
export interface AgoraTokenResponse {
    app_id: string;
    token: string | null;
    channel: string;
    uid: number;
}
