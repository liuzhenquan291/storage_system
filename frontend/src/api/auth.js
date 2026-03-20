import request from '@/utils/request'

// 登录
export const login = (data) => {
  return request.post('/auth/login', data)
}

// 登出
export const logout = () => {
  return request.post('/auth/logout')
}
