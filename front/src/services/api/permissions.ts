import apiClient from './index';

export interface RoleItem { id: string; name: string }
export interface PermissionItem { id: string; permission: string; title: string; category: string }
export interface RolePermissionLink { id: string; role: RoleItem; permission: PermissionItem }
export interface UserOverride {
  id: string;
  user: number;
  user_email: string;
  user_name: string | null;
  permission: PermissionItem;
  type: 'Add' | 'Remove';
  created_at: string;
}

export const getRoles = async () => (await apiClient.get<RoleItem[]>('/permissions/roles/')).data;
export const getPermissionDefinitions = async () =>
  (await apiClient.get<PermissionItem[]>('/permissions/permissions/')).data;
export const getRolePermissions = async () =>
  (await apiClient.get<RolePermissionLink[]>('/permissions/role-permissions/')).data;

export const grantRolePermission = async (roleId: string, permissionId: string) =>
  (await apiClient.post<RolePermissionLink>('/permissions/role-permissions/', { role_id: roleId, permission_id: permissionId })).data;
export const revokeRolePermission = async (linkId: string) => {
  await apiClient.delete(`/permissions/role-permissions/${linkId}/`);
};

export const getUserOverrides = async () =>
  (await apiClient.get<UserOverride[]>('/permissions/user-permissions/')).data;
export const addUserOverride = async (userId: number, permissionId: string, type: 'Add' | 'Remove') =>
  (await apiClient.post<UserOverride>('/permissions/user-permissions/', { user: userId, permission_id: permissionId, type })).data;
export const removeUserOverride = async (overrideId: string) => {
  await apiClient.delete(`/permissions/user-permissions/${overrideId}/`);
};
