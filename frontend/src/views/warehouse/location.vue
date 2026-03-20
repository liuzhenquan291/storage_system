<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">库位管理</h2>
      <el-button type="primary" @click="showBatchDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        批量创建库位
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="location_code" label="库位编号" width="150" />
      <el-table-column label="所属货架" width="180">
        <template #default="{ row }">
          {{ getShelfLabel(row.shelf_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="row_no" label="排" width="80" />
      <el-table-column prop="col_no" label="列" width="80" />
      <el-table-column prop="layer_no" label="层" width="80" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 2 ? 'warning' : row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 2 ? '占用' : row.status === 1 ? '空闲' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_time" label="创建时间" width="160" />
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
    
    <el-dialog v-model="batchDialogVisible" title="批量创建库位" width="500px">
      <el-form ref="batchFormRef" :model="batchForm" :rules="batchRules" label-width="100px">
        <el-form-item label="所属库房" prop="warehouse_id">
          <el-select v-model="batchForm.warehouse_id" placeholder="请选择所属库房" class="w-full" @change="onWarehouseChange">
            <el-option 
              v-for="item in warehouseOptions" 
              :key="item.id" 
              :label="item.label" 
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属货架" prop="shelf_id">
          <el-select v-model="batchForm.shelf_id" placeholder="请选择所属货架" class="w-full">
            <el-option 
              v-for="item in shelfOptions" 
              :key="item.id" 
              :label="item.label" 
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排数" prop="rows">
          <el-input-number v-model="batchForm.rows" :min="1" :max="99" />
        </el-form-item>
        <el-form-item label="列数" prop="cols">
          <el-input-number v-model="batchForm.cols" :min="1" :max="99" />
        </el-form-item>
        <el-form-item label="层数" prop="layers">
          <el-input-number v-model="batchForm.layers" :min="1" :max="99" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleBatchSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getLocations, batchCreateLocations, getWarehouseDropdown, getShelfDropdown } from '@/api/warehouse'

const loading = ref(false)
const submitLoading = ref(false)
const batchDialogVisible = ref(false)
const tableData = ref([])
const warehouseOptions = ref([])
const shelfOptions = ref([])
const shelfList = ref([])
const batchFormRef = ref()
const pagination = reactive({ page: 1, total: 0 })

const batchForm = reactive({ 
  warehouse_id: null,
  shelf_id: null, 
  rows: 5, 
  cols: 5, 
  layers: 5 
})

const batchRules = {
  warehouse_id: [{ required: true, message: '请选择所属库房', trigger: 'change' }],
  shelf_id: [{ required: true, message: '请选择所属货架', trigger: 'change' }],
  rows: [{ required: true }],
  cols: [{ required: true }],
  layers: [{ required: true }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getLocations({ page: pagination.page, page_size: 20 })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const loadWarehouseOptions = async () => {
  try {
    const res = await getWarehouseDropdown()
    warehouseOptions.value = res.data || []
  } catch (error) {
    console.error('加载库房列表失败:', error)
  }
}

const loadShelfOptions = async (warehouseId) => {
  if (!warehouseId) {
    shelfOptions.value = []
    return
  }
  try {
    const res = await getShelfDropdown({ warehouse_id: warehouseId })
    shelfOptions.value = res.data || []
  } catch (error) {
    console.error('加载货架列表失败:', error)
  }
}

const onWarehouseChange = (warehouseId) => {
  batchForm.shelf_id = null
  loadShelfOptions(warehouseId)
}

const getShelfLabel = (shelfId) => {
  const shelf = shelfList.value.find(s => s.id === shelfId)
  return shelf ? shelf.label : shelfId
}

const showBatchDialog = () => { 
  Object.assign(batchForm, { warehouse_id: null, shelf_id: null, rows: 5, cols: 5, layers: 5 })
  shelfOptions.value = []
  batchDialogVisible.value = true 
}

const handleBatchSubmit = async () => {
  const valid = await batchFormRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = await batchCreateLocations(batchForm)
    ElMessage.success(res.message || '创建成功')
    batchDialogVisible.value = false
    loadData()
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  loadData()
  loadWarehouseOptions()
})
</script>
