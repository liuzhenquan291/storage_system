<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">货架管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增货架
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="shelf_code" label="货架编号" width="120" />
      <el-table-column prop="shelf_name" label="货架名称" width="150" />
      <el-table-column label="所属库房" width="180">
        <template #default="{ row }">
          {{ getWarehouseLabel(row.warehouse_id) }}
        </template>
      </el-table-column>
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          {{ row.shelf_type === 1 ? '单伸位' : '双伸位' }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_time" label="创建时间" width="160" />
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
    
    <el-dialog v-model="dialogVisible" title="新增货架" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="货架编号">
          <el-input disabled placeholder="系统自动生成，格式：SF-0001" />
          <div class="text-gray-400 text-xs mt-1">货架编号由系统自动生成，格式：SF-0001</div>
        </el-form-item>
        <el-form-item label="货架名称" prop="shelf_name">
          <el-input v-model="formData.shelf_name" placeholder="请输入货架名称" />
        </el-form-item>
        <el-form-item label="所属库房" prop="warehouse_id">
          <el-select v-model="formData.warehouse_id" placeholder="请选择所属库房" class="w-full" @change="onWarehouseChange">
            <el-option 
              v-for="item in warehouseOptions" 
              :key="item.id" 
              :label="item.label" 
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属产线">
          <el-select v-model="formData.line_id" placeholder="请选择所属产线（可选）" class="w-full" clearable>
            <el-option 
              v-for="item in lineOptions" 
              :key="item.id" 
              :label="item.label" 
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="货架类型">
          <el-radio-group v-model="formData.shelf_type">
            <el-radio :value="1">单伸位</el-radio>
            <el-radio :value="2">双伸位</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getShelves, createShelf, getWarehouseDropdown, getLineDropdown } from '@/api/warehouse'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const tableData = ref([])
const warehouseOptions = ref([])
const lineOptions = ref([])
const formRef = ref()
const pagination = reactive({ page: 1, total: 0 })

const formData = reactive({ 
  shelf_name: '', 
  warehouse_id: null,
  line_id: null,
  shelf_type: 1 
})

const formRules = {
  shelf_name: [{ required: true, message: '请输入货架名称', trigger: 'blur' }],
  warehouse_id: [{ required: true, message: '请选择所属库房', trigger: 'change' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getShelves({ page: pagination.page, page_size: 20 })
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

const loadLineOptions = async (warehouseId) => {
  if (!warehouseId) {
    lineOptions.value = []
    return
  }
  try {
    const res = await getLineDropdown(warehouseId)
    lineOptions.value = res.data || []
  } catch (error) {
    console.error('加载产线列表失败:', error)
  }
}

const onWarehouseChange = (warehouseId) => {
  formData.line_id = null
  loadLineOptions(warehouseId)
}

const getWarehouseLabel = (warehouseId) => {
  const warehouse = warehouseOptions.value.find(w => w.id === warehouseId)
  return warehouse ? warehouse.label : warehouseId
}

const showDialog = () => { 
  Object.assign(formData, { shelf_name: '', warehouse_id: null, line_id: null, shelf_type: 1 })
  lineOptions.value = []
  dialogVisible.value = true 
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try { 
    await createShelf(formData)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('创建失败:', error)
  } finally { 
    submitLoading.value = false 
  }
}

onMounted(() => {
  loadData()
  loadWarehouseOptions()
})
</script>
