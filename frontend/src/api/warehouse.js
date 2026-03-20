import request from '@/utils/request'

// 库房管理
export const getWarehouses = (params) => request.get('/warehouse/info', { params })
export const getWarehouseDropdown = () => request.get('/warehouse/info/dropdown')
export const createWarehouse = (data) => request.post('/warehouse/info', data)
export const updateWarehouse = (id, data) => request.put(`/warehouse/info/${id}`, data)
export const deleteWarehouse = (id) => request.delete(`/warehouse/info/${id}`)

// 产线管理
export const getLines = (params) => request.get('/warehouse/line', { params })
export const getLineDropdown = (warehouseId) => request.get('/warehouse/line/dropdown', { params: { warehouse_id: warehouseId } })
export const createLine = (data) => request.post('/warehouse/line', data)

// 货架管理
export const getShelves = (params) => request.get('/warehouse/shelf', { params })
export const getShelfDropdown = (params) => request.get('/warehouse/shelf/dropdown', { params })
export const createShelf = (data) => request.post('/warehouse/shelf', data)

// 库位管理
export const getLocations = (params) => request.get('/warehouse/location', { params })
export const getLocationDropdown = (params) => request.get('/warehouse/location/dropdown', { params })
export const createLocation = (data) => request.post('/warehouse/location', data)
export const batchCreateLocations = (data) => request.post('/warehouse/location/batch', data)

// 获取编号前缀
export const getCodePrefixes = () => request.get('/warehouse/code-prefixes')
