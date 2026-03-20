<template>
  <div class="bg-white rounded-xl shadow-sm p-5">
    <h2 class="text-lg font-medium mb-4">出入库记录</h2>
    
    <el-form :inline="true" class="mb-4">
      <el-form-item label="操作类型">
        <el-select v-model="searchForm.operation_type" placeholder="全部" clearable>
          <el-option label="入库" :value="1" />
          <el-option label="出库" :value="2" />
        </el-select>
      </el-form-item>
      <el-form-item><el-button type="primary" @click="loadData">搜索</el-button></el-form-item>
    </el-form>
    
    <el-table :data="tableData" stripe v-loading="loading">
      <el-table-column prop="order_code" label="工单号" width="180" />
      <el-table-column label="类型" width="80">
        <template #default="{ row }">
          <el-tag :type="row.operation_type === 1 ? 'success' : 'warning'" size="small">
            {{ row.operation_type === 1 ? '入库' : '出库' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="material_name" label="物资" width="150" />
      <el-table-column prop="quantity" label="数量" width="80" />
      <el-table-column prop="before_quantity" label="操作前" width="80" />
      <el-table-column prop="after_quantity" label="操作后" width="80" />
      <el-table-column prop="operator_name" label="操作人" width="100" />
      <el-table-column prop="operation_time" label="操作时间" width="160" />
    </el-table>
    
    <el-pagination class="mt-4 justify-end" v-model:current-page="pagination.page" :total="pagination.total" layout="total, prev, pager, next" @change="loadData" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getInoutRecords } from '@/api/order'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, total: 0 })
const searchForm = reactive({ operation_type: null })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getInoutRecords({ page: pagination.page, page_size: 20, ...searchForm })
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } finally { loading.value = false }
}

onMounted(() => loadData())
</script>
