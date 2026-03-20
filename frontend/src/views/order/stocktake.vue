<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-medium">盘点任务</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon class="mr-1"><Plus /></el-icon>
        新增盘点
      </el-button>
    </div>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="order_code" label="工单号" width="180" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusMap[row.status]?.type" size="small">{{ statusMap[row.status]?.label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="plan_quantity" label="物资数量" width="100" />
      <el-table-column prop="operator_name" label="操作人" width="100" />
      <el-table-column prop="created_time" label="创建时间" width="160" />
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getStocktakeOrders, createStocktakeOrder } from '@/api/order'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, total: 0 })

const statusMap = { 0: { label: '待执行', type: 'info' }, 1: { label: '执行中', type: 'warning' }, 2: { label: '已完成', type: 'success' }, 3: { label: '已取消', type: 'danger' } }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getStocktakeOrders({ page: pagination.page, page_size: 20 })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally { loading.value = false }
}

const handleCreate = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入库房ID', '新增盘点任务', { inputPattern: /^\d+$/, inputErrorMessage: '请输入有效的库房ID' })
    await createStocktakeOrder({ warehouse_id: parseInt(value) })
    ElMessage.success('创建成功')
    loadData()
  } catch (error) { console.error(error) }
}

onMounted(() => loadData())
</script>
