<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">出库任务</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增出库
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="order_code" label="工单号" width="180" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusMap[row.status]?.type" size="small">{{ statusMap[row.status]?.label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="plan_quantity" label="计划数量" width="100" />
      <el-table-column prop="actual_quantity" label="实际数量" width="100" />
      <el-table-column prop="operator_name" label="操作人" width="100" />
      <el-table-column prop="created_time" label="创建时间" width="160" />
      <el-table-column prop="end_time" label="完成时间" width="160" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 0" type="success" size="small" @click="handleExecute(row)">执行</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
    
    <el-dialog v-model="dialogVisible" title="新增出库任务" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="库房ID" prop="warehouse_id">
          <el-input-number v-model="formData.warehouse_id" :min="1" />
        </el-form-item>
        <el-form-item label="物资明细">
          <div v-for="(item, index) in formData.items" :key="index" class="flex gap-2 mb-2">
            <el-input v-model="item.material_code" placeholder="物资编号" style="width:120px" />
            <el-input v-model="item.material_name" placeholder="物资名称" style="width:120px" />
            <el-input-number v-model="item.quantity" placeholder="数量" :min="1" style="width:100px" />
            <el-input-number v-model="item.stock_id" placeholder="库存ID" :min="1" style="width:100px" />
            <el-button type="danger" :icon="Delete" circle @click="formData.items.splice(index, 1)" />
          </div>
          <el-button type="primary" text @click="formData.items.push({})">添加物资</el-button>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" />
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
import { Plus, Delete } from '@element-plus/icons-vue'
import { getOutboundOrders, createOutboundOrder, executeOutboundOrder } from '@/api/order'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const tableData = ref([])
const formRef = ref()
const pagination = reactive({ page: 1, total: 0 })

const statusMap = { 0: { label: '待执行', type: 'info' }, 1: { label: '执行中', type: 'warning' }, 2: { label: '已完成', type: 'success' }, 3: { label: '已取消', type: 'danger' } }
const formData = reactive({ warehouse_id: null, items: [{}], remark: '' })
const formRules = { warehouse_id: [{ required: true, message: '请输入库房ID', trigger: 'blur' }] }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getOutboundOrders({ page: pagination.page, page_size: 20 })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally { loading.value = false }
}

const showDialog = () => { Object.assign(formData, { warehouse_id: null, items: [{}], remark: '' }); dialogVisible.value = true }

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try { await createOutboundOrder(formData); ElMessage.success('创建成功'); dialogVisible.value = false; loadData() }
  finally { submitLoading.value = false }
}

const handleExecute = async (row) => {
  try {
    await ElMessageBox.confirm('确定执行该出库任务？', '提示', { type: 'warning' })
    await executeOutboundOrder(row.id)
    ElMessage.success('执行成功')
    loadData()
  } catch (error) { console.error(error) }
}

onMounted(() => loadData())
</script>
