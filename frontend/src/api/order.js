import request from '@/utils/request'

// 入库任务
export const getInboundOrders = (params) => request.get('/orders/inbound', { params })
export const createInboundOrder = (data) => request.post('/orders/inbound', data)
export const executeInboundOrder = (id) => request.post(`/orders/inbound/${id}/execute`)

// 出库任务
export const getOutboundOrders = (params) => request.get('/orders/outbound', { params })
export const createOutboundOrder = (data) => request.post('/orders/outbound', data)
export const executeOutboundOrder = (id) => request.post(`/orders/outbound/${id}/execute`)

// 盘点任务
export const getStocktakeOrders = (params) => request.get('/orders/stocktake', { params })
export const createStocktakeOrder = (data) => request.post('/orders/stocktake', data)

// 出入库记录
export const getInoutRecords = (params) => request.get('/orders/records', { params })
