// Based on backend/app/schemas/token.py
export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

// For login form data (OAuth2PasswordRequestForm)
export interface LoginPayload {
  username: string; // Corresponds to email in our case
  password: string;
}
