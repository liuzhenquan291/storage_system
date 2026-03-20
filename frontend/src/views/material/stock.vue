<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <h2 class="text-lg font-medium mb-4">在库物资</h2>
    
    <el-form :inline="true" class="mb-4">
      <el-form-item label="物资名称"><el-input v-model="searchForm.material_name" clearable /></el-form-item>
      <el-form-item><el-button type="primary" @click="loadData">搜索</el-button></el-form-item>
    </el-form>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="material_code" label="物资编号" width="120" />
      <el-table-column prop="material_name" label="物资名称" width="150" />
      <el-table-column prop="quantity" label="数量" width="100" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column prop="batch_no" label="批次号" width="120" />
      <el-table-column prop="location_id" label="库位ID" width="100" />
      <el-table-column prop="inbound_time" label="入库时间" width="160" />
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getMaterialStocks } from '@/api/material'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, total: 0 })
const searchForm = reactive({ material_name: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMaterialStocks({ page: pagination.page, page_size: 20, ...searchForm })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(() => loadData())
</script>
