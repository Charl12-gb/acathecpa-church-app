import { User } from './userTypes';
import { UserRole } from './userTypes';

export interface SocialLinks {
  linkedin?: string | null;
  twitter?: string | null;
  github?: string | null;
  website?: string | null;
  orcid?: string | null;
  google_scholar?: string | null;
}

export interface EducationEntry {
  institution: string;
  degree: string;
  field_of_study?: string | null;
  start_year?: number | null;
  end_year?: number | null;
  description?: string | null;
}

export interface ExperienceEntry {
  company: string;
  role: string;
  start_date?: string | null;
  end_date?: string | null;
  description?: string | null;
}

export interface ProfessorProfile {
  id: number; // ID du Profil
  user_id: number;
  specialization: string;
  bio?: string | null;
  education?: EducationEntry[];
  experience?: ExperienceEntry[];
  skills?: string[];
  social_links?: SocialLinks;
}

export interface Professor {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  country?: string | null;
  birthdate?: string | null;
  is_active: boolean;
  role: UserRole; 
  professor_profile: ProfessorProfile | null;
}

export interface ProfessorUserAndProfileCreatePayload {
  name: string;
  email: string;
  password?: string; // Requis pour un nouvel utilisateur
  phone?: string | null;
  country?: string | null;
  birthdate?: string | null;
  is_active?: boolean;

  // Partie Profil (plate)
  specialization: string;
  bio?: string | null;
  education?: EducationEntry[];
  experience?: ExperienceEntry[];
  skills?: string[];
  social_links?: SocialLinks;
}

export interface ProfessorProfileUpdatePayload {
  specialization?: string;
  bio?: string | null;
  education?: EducationEntry[];
  experience?: ExperienceEntry[];
  skills?: string[];
  social_links?: SocialLinks;
}

export interface ProfessorProfileCreatePayload {
  specialization: string;
  bio: string;
  education?: EducationEntry[];
  experience?: ExperienceEntry[];
  skills?: string[];
  social_links?: SocialLinks;
}

export interface Professor extends User {
  professor_profile: ProfessorProfile | null;
}
