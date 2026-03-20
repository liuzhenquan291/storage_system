<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">角色管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增角色
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="role_name" label="角色名称" width="150" />
      <el-table-column prop="role_code" label="角色编码" width="150" />
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column label="权限数量" width="100">
        <template #default="{ row }">
          <el-tag type="info" size="small">{{ row.permission_count || 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_time" label="创建时间" width="160" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="showDialog(row)">编辑</el-button>
          <el-button text type="success" @click="showPermissionDialog(row)">权限</el-button>
          <el-button text type="danger" @click="handleDelete(row)" :disabled="row.role_code === 'super_admin'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      class="mt-4 justify-end"
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      layout="total, prev, pager, next"
      @change="loadData"
    />
    
    <!-- 新增/编辑角色对话框 -->
    <el-dialog v-model="dialogVisible" :title="formData.id ? '编辑角色' : '新增角色'" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="角色名称" prop="role_name">
          <el-input v-model="formData.role_name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="role_code">
          <el-input v-model="formData.role_code" :disabled="!!formData.id" placeholder="请输入角色编码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 权限分配对话框 -->
    <el-dialog v-model="permissionDialogVisible" title="分配权限" width="600px">
      <div class="mb-4">
        <span class="text-gray-500">角色：{{ currentRole?.role_name }}</span>
      </div>
      <el-checkbox-group v-model="selectedPermissions">
        <div v-for="group in permissionGroups" :key="group.name" class="mb-4">
          <div class="font-medium text-gray-700 mb-2">{{ group.name }}</div>
          <div class="flex flex-wrap gap-2">
            <el-checkbox 
              v-for="perm in group.permissions" 
              :key="perm.code" 
              :value="perm.code"
              :label="perm.code"
            >
              {{ perm.name }}
            </el-checkbox>
          </div>
        </div>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="permissionLoading" @click="handleSavePermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getRoles, createRole, updateRole, deleteRole, getRolePermissions, updateRolePermissions } from '@/api/role'
import { getResources } from '@/api/resource'

const loading = ref(false)
const submitLoading = ref(false)
const permissionLoading = ref(false)
const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const tableData = ref([])
const formRef = ref()
const currentRole = ref(null)
const allResources = ref([])
const selectedPermissions = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const formData = reactive({
  id: null,
  role_name: '',
  role_code: '',
  description: ''
})

const formRules = {
  role_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  role_code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
}

// 权限分组
const permissionGroups = computed(() => {
  const groups = {
    '仪表盘': [],
    '用户管理': [],
    '角色管理': [],
    '库房管理': [],
    '物资管理': [],
    '工单管理': [],
    '设备管理': []
  }
  
  allResources.value.forEach(r => {
    if (r.code.startsWith('dashboard')) groups['仪表盘'].push(r)
    else if (r.code.startsWith('user')) groups['用户管理'].push(r)
    else if (r.code.startsWith('role')) groups['角色管理'].push(r)
    else if (r.code.startsWith('warehouse')) groups['库房管理'].push(r)
    else if (r.code.startsWith('material')) groups['物资管理'].push(r)
    else if (r.code.startsWith('order') || r.code.startsWith('record')) groups['工单管理'].push(r)
    else if (r.code.startsWith('device')) groups['设备管理'].push(r)
  })
  
  return Object.entries(groups)
    .filter(([_, perms]) => perms.length > 0)
    .map(([name, permissions]) => ({ name, permissions }))
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getRoles({ page: pagination.page, page_size: pagination.pageSize })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadResources = async () => {
  try {
    const res = await getResources()
    allResources.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

const showDialog = (row) => {
  if (row) {
    Object.assign(formData, row)
  } else {
    Object.assign(formData, { id: null, role_name: '', role_code: '', description: '' })
  }
  dialogVisible.value = true
}

const showPermissionDialog = async (row) => {
  if (row.role_code === 'super_admin') {
    ElMessage.warning('超级管理员拥有所有权限，无需配置')
    return
  }
  
  currentRole.value = row
  permissionDialogVisible.value = true
  
  // 加载角色当前权限
  try {
    const res = await getRolePermissions(row.id)
    selectedPermissions.value = res.data || []
  } catch (error) {
    console.error(error)
    selectedPermissions.value = []
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitLoading.value = true
  try {
    if (formData.id) {
      await updateRole(formData.id, formData.role_name, formData.description)
      ElMessage.success('更新成功')
    } else {
      await createRole(formData.role_name, formData.role_code, formData.description)
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

const handleSavePermissions = async () => {
  permissionLoading.value = true
  try {
    await updateRolePermissions(currentRole.value.id, selectedPermissions.value)
    ElMessage.success('权限保存成功')
    permissionDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    permissionLoading.value = false
  }
}

const handleDelete = async (row) => {
  if (row.role_code === 'super_admin') {
    ElMessage.warning('超级管理员角色不能删除')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定删除该角色？', '提示', { type: 'warning' })
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadData()
  loadResources()
})
</script>
