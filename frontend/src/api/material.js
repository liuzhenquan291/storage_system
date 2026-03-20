import request from '@/utils/request'

// 物资类型
export const getMaterialTypes = (params) => request.get('/materials/type', { params })
export const createMaterialType = (data) => request.post('/materials/type', data)

// 在库物资
export const getMaterialStocks = (params) => request.get('/materials/stock', { params })
export const getMaterialStockDetail = (id) => request.get(`/materials/stock/${id}`)

// 出库记录
export const getOutboundRecords = (params) => request.get('/materials/outbound-record', { params })

// 料箱管理
export const getMaterialBoxes = (params) => request.get('/materials/box', { params })
export const createMaterialBox = (data) => request.post('/materials/box', data)
