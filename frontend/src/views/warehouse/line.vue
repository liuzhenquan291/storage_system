<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">产线管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增产线
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="line_code" label="产线编号" width="120" />
      <el-table-column prop="line_name" label="产线名称" width="150" />
      <el-table-column label="所属库房" width="180">
        <template #default="{ row }">
          {{ getWarehouseLabel(row.warehouse_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" />
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
    
    <el-dialog v-model="dialogVisible" title="新增产线" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="产线编号">
          <el-input disabled placeholder="系统自动生成，格式：PL-0001" />
          <div class="text-gray-400 text-xs mt-1">产线编号由系统自动生成，格式：PL-0001</div>
        </el-form-item>
        <el-form-item label="产线名称" prop="line_name">
          <el-input v-model="formData.line_name" placeholder="请输入产线名称" />
        </el-form-item>
        <el-form-item label="所属库房" prop="warehouse_id">
          <el-select v-model="formData.warehouse_id" placeholder="请选择所属库房" class="w-full">
            <el-option 
              v-for="item in warehouseOptions" 
              :key="item.id" 
              :label="item.label" 
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" placeholder="请输入描述（可选）" />
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
import { getLines, createLine, getWarehouseDropdown } from '@/api/warehouse'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const tableData = ref([])
const warehouseOptions = ref([])
const formRef = ref()
const pagination = reactive({ page: 1, total: 0 })

const formData = reactive({
  line_name: '',
  warehouse_id: null,
  description: ''
})

const formRules = {
  line_name: [{ required: true, message: '请输入产线名称', trigger: 'blur' }],
  warehouse_id: [{ required: true, message: '请选择所属库房', trigger: 'change' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getLines({ page: pagination.page, page_size: 20 })
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

const getWarehouseLabel = (warehouseId) => {
  const warehouse = warehouseOptions.value.find(w => w.id === warehouseId)
  return warehouse ? warehouse.label : warehouseId
}

const showDialog = () => {
  Object.assign(formData, { line_name: '', warehouse_id: null, description: '' })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    await createLine(formData)
    ElMessage.success('创建成功')
    dialogVisible.value = false
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
