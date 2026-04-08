import { api } from './api';

export interface LoginResponse {
  access_token: string;
}

export interface User {
  id: number;
  email: string;
  name: string;
  is_admin: boolean;
}

export const authService = {
  register: (email: string, password: string, name: string) =>
    api.post<void>('/auth/register', { email, password, name }),

  login: async (email: string, password: string): Promise<void> => {
    const data = await api.post<LoginResponse>('/auth/login', { email, password });
    localStorage.setItem('token', data.access_token);
  },

  logout: () => localStorage.removeItem('token'),

  me: () => api.get<User>('/users/me'),

  isLoggedIn: () => !!localStorage.getItem('token'),
};
