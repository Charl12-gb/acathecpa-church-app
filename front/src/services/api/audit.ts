import apiClient from './index';

export interface AuditEntry {
  id: number;
  created_at: string;
  actor_email: string;
  action: string;
  action_label: string;
  target_type: string;
  target_id: string;
  target_label: string;
  details: Record<string, any>;
}

/** Super admins only. */
export const getAuditLogs = async (params: { action?: string; q?: string; limit?: number } = {}) =>
  (await apiClient.get<AuditEntry[]>('/audit-logs', { params })).data;
