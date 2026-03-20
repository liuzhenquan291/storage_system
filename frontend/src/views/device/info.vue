<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">设备信息</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增设备
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="device_code" label="设备编号" width="120" />
      <el-table-column prop="device_name" label="设备名称" width="150" />
      <el-table-column prop="type_id" label="类型ID" width="100" />
      <el-table-column prop="ip_address" label="IP地址" width="140" />
      <el-table-column prop="port" label="端口" width="80" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '在线' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_time" label="创建时间" width="160" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="showDialog(row)">编辑</el-button>
          <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
    
    <el-dialog v-model="dialogVisible" :title="formData.id ? '编辑设备' : '新增设备'" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="编号" prop="device_code"><el-input v-model="formData.device_code" :disabled="!!formData.id" /></el-form-item>
        <el-form-item label="名称" prop="device_name"><el-input v-model="formData.device_name" /></el-form-item>
        <el-form-item label="类型ID" prop="type_id"><el-input-number v-model="formData.type_id" :min="1" /></el-form-item>
        <el-form-item label="库房ID"><el-input-number v-model="formData.warehouse_id" :min="1" /></el-form-item>
        <el-form-item label="IP地址"><el-input v-model="formData.ip_address" /></el-form-item>
        <el-form-item label="端口"><el-input-number v-model="formData.port" :min="1" :max="65535" /></el-form-item>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getDevices, createDevice, updateDevice, deleteDevice } from '@/api/device'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const tableData = ref([])
const formRef = ref()
const pagination = reactive({ page: 1, total: 0 })

const formData = reactive({ id: null, device_code: '', device_name: '', type_id: null, warehouse_id: null, ip_address: '', port: null, description: '' })
const formRules = {
  device_code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  device_name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  type_id: [{ required: true, message: '请输入类型ID', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getDevices({ page: pagination.page, page_size: 20 })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally { loading.value = false }
}

const showDialog = (row) => {
  if (row) { Object.assign(formData, row) }
  else { Object.assign(formData, { id: null, device_code: '', device_name: '', type_id: null, warehouse_id: null, ip_address: '', port: null, description: '' }) }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (formData.id) { await updateDevice(formData.id, formData); ElMessage.success('更新成功') }
    else { await createDevice(formData); ElMessage.success('创建成功') }
    dialogVisible.value = false; loadData()
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该设备？', '提示', { type: 'warning' })
    await deleteDevice(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) { console.error(error) }
}

onMounted(() => loadData())
</script>
