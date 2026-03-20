<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">物资类型</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增类型
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="type_code" label="类型编码" width="120" />
      <el-table-column prop="type_name" label="类型名称" width="150" />
      <el-table-column prop="specification" label="规格" width="150" />
      <el-table-column prop="unit" label="单位" width="80" />
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
    
    <el-dialog v-model="dialogVisible" title="新增物资类型" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="编码" prop="type_code"><el-input v-model="formData.type_code" /></el-form-item>
        <el-form-item label="名称" prop="type_name"><el-input v-model="formData.type_name" /></el-form-item>
        <el-form-item label="规格"><el-input v-model="formData.specification" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="formData.unit" /></el-form-item>
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
import { getMaterialTypes, createMaterialType } from '@/api/material'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const tableData = ref([])
const formRef = ref()
const pagination = reactive({ page: 1, total: 0 })

const formData = reactive({ type_code: '', type_name: '', specification: '', unit: '', description: '' })
const formRules = {
  type_code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  type_name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMaterialTypes({ page: pagination.page, page_size: 20 })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const showDialog = () => { Object.assign(formData, { type_code: '', type_name: '', specification: '', unit: '', description: '' }); dialogVisible.value = true }

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try { await createMaterialType(formData); ElMessage.success('创建成功'); dialogVisible.value = false; loadData() }
  finally { submitLoading.value = false }
}

onMounted(() => loadData())
</script>
