import { apiClient } from './client';
import type { Preference, PreferencesPayload } from '../types';

export const getPreferences = () =>
  apiClient.get<Preference>('/preferences');

export const updatePreferences = (payload: PreferencesPayload) =>
  apiClient.put<Preference>('/preferences', payload);
