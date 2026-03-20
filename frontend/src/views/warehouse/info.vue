<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">库房管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增库房
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="warehouse_code" label="库房编号" width="120" />
      <el-table-column prop="warehouse_name" label="库房名称" width="150" />
      <el-table-column prop="address" label="地址" min-width="200" />
      <el-table-column prop="description" label="描述" min-width="150" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '启用' : '停用' }}
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
    
    <el-pagination
      class="mt-4 justify-end"
      v-model:current-page="pagination.page"
      :total="pagination.total"
      layout="total, prev, pager, next"
      @change="loadData"
    />
    
    <el-dialog v-model="dialogVisible" :title="formData.id ? '编辑库房' : '新增库房'" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="库房编号" v-if="formData.id">
          <el-input v-model="formData.warehouse_code" disabled />
        </el-form-item>
        <el-form-item label="库房编号" v-else>
          <el-input disabled placeholder="系统自动生成，格式：WH-0001" />
          <div class="text-gray-400 text-xs mt-1">库房编号由系统自动生成，格式：WH-0001</div>
        </el-form-item>
        <el-form-item label="库房名称" prop="warehouse_name">
          <el-input v-model="formData.warehouse_name" placeholder="请输入库房名称" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="formData.address" placeholder="请输入地址（可选）" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" placeholder="请输入描述（可选）" />
        </el-form-item>
        <el-form-item label="状态" v-if="formData.id">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">停用</el-radio>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getWarehouses, createWarehouse, updateWarehouse, deleteWarehouse } from '@/api/warehouse'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const tableData = ref([])
const formRef = ref()

const pagination = reactive({ page: 1, total: 0 })

const formData = reactive({
  id: null,
  warehouse_code: '',
  warehouse_name: '',
  address: '',
  description: '',
  status: 1
})

const formRules = {
  warehouse_name: [{ required: true, message: '请输入库房名称', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getWarehouses({ page: pagination.page, page_size: 20 })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const showDialog = (row) => {
  if (row) {
    Object.assign(formData, row)
  } else {
    Object.assign(formData, { id: null, warehouse_code: '', warehouse_name: '', address: '', description: '', status: 1 })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitLoading.value = true
  try {
    if (formData.id) {
      await updateWarehouse(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createWarehouse(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该库房？', '提示', { type: 'warning' })
    await deleteWarehouse(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => loadData())
</script>
