export type UserRole = "tourist" | "student" | "local" | "admin";

export interface AuthorBrief {
  id: number;
  display_name: string | null;
  avatar_url: string | null;
  role: string;
}

export interface UserProfile {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  profile_completed: boolean;
  missing_fields: string[];
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  profile_completed: boolean;
  missing_fields: string[];
}

export interface CommunityAccess {
  authenticated: boolean;
  profile_completed: boolean;
  can_enter_community: boolean;
  missing_fields: string[];
  user: UserProfile | null;
}

export interface Post {
  id: number;
  author_id: number;
  author: AuthorBrief | null;
  title: string | null;
  body: string;
  location_name: string | null;
  topic_tags: string | null;
  created_at: string;
}

export interface Comment {
  id: number;
  post_id: number;
  author_id: number;
  author: AuthorBrief | null;
  body: string;
  created_at: string;
}

export interface PostDetail extends Post {
  comments: Comment[];
}

export interface GenerationJob {
  id: number;
  user_id: number;
  prompt: string;
  count: number;
  format: string;
  status: string;
  created_at: string;
  completed_at: string | null;
}

export interface AnnotationResult {
  text: string;
  category: string;
  sentiment: string;
  topic_tags: string[];
}

export interface QualityEvalResult {
  job_id: number;
  overall_score: number;
  metrics: Record<string, unknown>;
  eval_profile: string;
}
