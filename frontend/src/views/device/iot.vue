<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">IOT设备</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增设备
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="device_code" label="设备编号" width="120" />
      <el-table-column prop="device_name" label="设备名称" width="150" />
      <el-table-column label="设备类型" width="120">
        <template #default="{ row }">
          {{ deviceTypeMap[row.device_type] || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="ip_address" label="IP地址" width="140" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '在线' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_time" label="创建时间" width="160" />
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
    
    <el-dialog v-model="dialogVisible" title="新增IOT设备" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="编号" prop="device_code"><el-input v-model="formData.device_code" /></el-form-item>
        <el-form-item label="名称" prop="device_name"><el-input v-model="formData.device_name" /></el-form-item>
        <el-form-item label="类型" prop="device_type">
          <el-select v-model="formData.device_type">
            <el-option label="摄像头" :value="1" />
            <el-option label="温湿度传感器" :value="2" />
            <el-option label="大屏" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="库房ID"><el-input-number v-model="formData.warehouse_id" :min="1" /></el-form-item>
        <el-form-item label="IP地址"><el-input v-model="formData.ip_address" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="formData.description" type="textarea" /></el-form-item>
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
import { getIotDevices, createIotDevice } from '@/api/device'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const tableData = ref([])
const formRef = ref()
const pagination = reactive({ page: 1, total: 0 })

const deviceTypeMap = { 1: '摄像头', 2: '温湿度传感器', 3: '大屏' }
const formData = reactive({ device_code: '', device_name: '', device_type: 1, warehouse_id: null, ip_address: '', description: '' })
const formRules = {
  device_code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  device_name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  device_type: [{ required: true, message: '请选择类型', trigger: 'change' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getIotDevices({ page: pagination.page, page_size: 20 })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally { loading.value = false }
}

const showDialog = () => {
  Object.assign(formData, { device_code: '', device_name: '', device_type: 1, warehouse_id: null, ip_address: '', description: '' })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try { await createIotDevice(formData); ElMessage.success('创建成功'); dialogVisible.value = false; loadData() }
  finally { submitLoading.value = false }
}

onMounted(() => loadData())
</script>
