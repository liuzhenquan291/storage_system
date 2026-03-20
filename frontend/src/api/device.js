import request from '@/utils/request'

// 设备类型
export const getDeviceTypes = () => request.get('/devices/type')
export const createDeviceType = (data) => request.post('/devices/type', data)

// 设备信息
export const getDevices = (params) => request.get('/devices/info', { params })
export const createDevice = (data) => request.post('/devices/info', data)
export const updateDevice = (id, data) => request.put(`/devices/info/${id}`, data)
export const deleteDevice = (id) => request.delete(`/devices/info/${id}`)

// IOT设备
export const getIotDevices = (params) => request.get('/devices/iot', { params })
export const createIotDevice = (data) => request.post('/devices/iot', data)
