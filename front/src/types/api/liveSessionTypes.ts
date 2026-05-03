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
  scheduled_for: string;
  duration_minutes?: number | null;
  host_id: number;
  host?: User | null;
  status: LiveSessionStatus;
  actual_started_at?: string | null;
  actual_ended_at?: string | null;
  meeting_room_name?: string | null;
}

export interface LiveSessionCreatePayload {
  course_id?: number | null;
  title: string;
  description?: string;
  scheduled_for: string;
  duration_minutes?: number;
  meeting_room_name?: string;
}

export interface LiveSessionUpdatePayload {
  title?: string;
  description?: string;
  scheduled_for?: string;
  duration_minutes?: number;
  status?: LiveSessionStatus;
  meeting_room_name?: string;
}

export interface LiveSessionReschedulePayload {
  scheduled_for: string;
  duration_minutes?: number;
  title?: string;
  description?: string;
}

export interface LiveSessionAttendanceMember {
  user_id: number;
  user_name?: string | null;
  user_email?: string | null;
  first_joined_at?: string | null;
  last_joined_at?: string | null;
  last_left_at?: string | null;
  total_duration_seconds: number;
  join_count: number;
  is_present: boolean;
}

export interface LiveSessionAttendanceSummary {
  session_id: number;
  title: string;
  status: LiveSessionStatus;
  scheduled_for: string;
  planned_duration_minutes?: number | null;
  actual_started_at?: string | null;
  actual_ended_at?: string | null;
  actual_duration_seconds: number;
  unique_attendees: number;
  present_count: number;
  expected_attendees?: number | null;
  attendance_rate?: number | null;
  attendees: LiveSessionAttendanceMember[];
}

export interface JitsiJoinResponse {
  app_id: string;
  domain: string;
  room: string;
  url: string;
  jwt: string | null;
  uid: number;
}
