<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <h2 class="text-lg font-medium mb-4">出库记录</h2>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="material_code" label="物资编号" width="120" />
      <el-table-column prop="material_name" label="物资名称" width="150" />
      <el-table-column prop="quantity" label="出库数量" width="100" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column prop="operator_name" label="操作人" width="100" />
      <el-table-column prop="outbound_time" label="出库时间" width="160" />
      <el-table-column prop="order_id" label="工单ID" width="100" />
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getOutboundRecords } from '@/api/material'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, total: 0 })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getOutboundRecords({ page: pagination.page, page_size: 20 })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(() => loadData())
</script>
