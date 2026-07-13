export interface TeamMemberSocialLinks {
  linkedin?: string;
  twitter?: string;
  facebook?: string;
  email?: string;
  website?: string;
}

export interface TeamMember {
  id: number;
  name: string;
  title: string;
  photo_url?: string | null;
  bio?: string | null;
  social_links: TeamMemberSocialLinks;
  order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TeamMemberPayload {
  name: string;
  title: string;
  photo_url?: string | null;
  bio?: string | null;
  social_links?: TeamMemberSocialLinks;
  order?: number;
  is_active?: boolean;
}
