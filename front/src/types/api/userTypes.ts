export enum UserRole {
  STUDENT = 'student',
  PROFESSOR = 'professor',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin',
}

export interface User {
  id: number;
  email: string;
  name: string;
  phone?: string | null;
  role: UserRole;
  country?: string | null;
  birthdate?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreatePayload {
  email: string;
  name: string;
  password: string;
  phone?: string;
  country?: string;
  birthdate?: string;
  role?: UserRole;
}

export interface UserUpdatePayload {
  email?: string;
  name?: string;
  phone?: string | null;
  country?: string | null;
  birthdate?: string | null;
  role?: UserRole;
  is_active?: boolean;
  password?: string;
}
