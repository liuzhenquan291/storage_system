import request from '@/utils/request'

// 获取概览数据
export const getOverview = () => request.get('/dashboard/overview')

// 获取出入库趋势图
export const getInboundOutboundChart = (days = 7) => 
  request.get('/dashboard/chart/inbound-outbound', { params: { days } })

// 获取最近记录
export const getRecentRecords = (limit = 10) => 
  request.get('/dashboard/recent-records', { params: { limit } })
