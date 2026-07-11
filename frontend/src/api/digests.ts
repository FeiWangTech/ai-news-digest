import { apiClient } from './client';
import type { Digest, DigestListResponse } from '../types';

export const listDigests = (page = 1, pageSize = 20) =>
  apiClient.get<DigestListResponse>('/digests', {
    params: { page, page_size: pageSize },
  });

export const getDigest = (id: string) =>
  apiClient.get<Digest>(`/digests/${id}`);

export const generateDigest = () =>
  apiClient.post('/digests/generate');
