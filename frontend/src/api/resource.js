import request from '@/utils/request'

// 获取所有资源
export const getResources = () => {
  return request.get('/resources')
}

// 获取当前用户权限
export const getMyPermissions = () => {
  return request.get('/resources/my')
}
