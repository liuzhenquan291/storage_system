import request from '@/utils/request'

// 获取角色列表
export const getRoles = (params) => {
  return request.get('/roles', { params })
}

// 获取所有角色（下拉选择用）
export const getAllRoles = () => {
  return request.get('/roles/all')
}

// 创建角色
export const createRole = (role_name, role_code, description, permissions) => {
  return request.post('/roles', { role_name, role_code, description, permissions })
}

// 更新角色
export const updateRole = (id, role_name, description) => {
  return request.put(`/roles/${id}`, { role_name, description })
}

// 删除角色
export const deleteRole = (id) => {
  return request.delete(`/roles/${id}`)
}

// 获取角色权限
export const getRolePermissions = (roleId) => {
  return request.get(`/roles/${roleId}/permissions`)
}

// 更新角色权限
export const updateRolePermissions = (roleId, permissions) => {
  return request.put(`/roles/${roleId}/permissions`, permissions)
}
