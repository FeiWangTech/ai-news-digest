import { apiClient } from './client';
import type { RegisterPayload, LoginPayload, ChangePasswordPayload } from '../types';

export const register = (payload: RegisterPayload) =>
  apiClient.post('/auth/register', payload);

export const login = (payload: LoginPayload) =>
  apiClient.post('/auth/login', payload);

export const refresh = () =>
  apiClient.post('/auth/refresh');

export const getMe = () =>
  apiClient.get('/auth/me');

export const changePassword = (payload: ChangePasswordPayload) =>
  apiClient.post('/auth/change-password', payload);
