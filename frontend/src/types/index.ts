/** TypeScript interfaces matching backend schemas */

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface TokenRefreshResponse {
  access_token: string;
  refresh_token: string;
}

export interface Preference {
  id: string;
  email_time: string;
  timezone: string;
  frequency: string;
  sources: string[];
  topics: string[];
  subscribed: boolean;
  created_at: string;
  updated_at: string;
}

export interface DigestItem {
  id: string;
  subject: string;
  date: string;
  status: string;
  content?: string;
  article_title?: string;
  article_url?: string;
  summary?: string;
}

export interface Digest {
  id: string;
  subject: string;
  html_content: string;
  sent_at: string;
  status: string;
  items: DigestItem[];
}

export interface DigestListResponse {
  items: {
    id: string;
    subject: string;
    sent_at: string;
    status: string;
  }[];
  total: number;
  page: number;
  page_size: number;
}

export interface RegisterPayload {
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

export interface PreferencesPayload {
  email_time: string;
  timezone: string;
  frequency: string;
  sources: string[];
  topics: string[];
  subscribed: boolean;
}
