export enum UserRole {
  STUDENT = 'student',
  PROFESSOR = 'professor',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin',
}

export interface User {
  id: number;
  email: string;
  name?: string | null;
  phone?: string | null;
  role: UserRole;
  country?: string | null;
  birthdate?: string | null; // Consider Date object if consistently used
  is_active: boolean;
  created_at: string; // Or Date
  updated_at: string; // Or Date
}

export interface UserCreatePayload {
  email: string;
  name: string; // Required for registration
  password: string;
  phone?: string;
  country?: string;
  birthdate?: string;
  role?: UserRole; // Optional, backend might default
}

export interface UserUpdatePayload {
  email?: string;
  name?: string;
  phone?: string;
  country?: string;
  birthdate?: string;
  role?: UserRole;
  is_active?: boolean;
  password?: string; // For password changes
}
