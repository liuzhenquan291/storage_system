<template>
  <div class="space-y-4">
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div 
        v-for="stat in statistics" 
        :key="stat.title"
        class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">{{ stat.title }}</p>
            <p class="text-2xl font-semibold mt-1" :class="stat.color">
              {{ stat.value }}
            </p>
            <p v-if="stat.subtitle" class="text-xs text-gray-400 mt-1">
              {{ stat.subtitle }}
            </p>
          </div>
          <div 
            class="w-12 h-12 rounded-xl flex items-center justify-center"
            :class="stat.bgColor"
          >
            <el-icon :size="24" :class="stat.color">
              <component :is="stat.icon" />
            </el-icon>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- 出入库趋势 -->
      <div class="bg-white rounded-xl p-5 shadow-sm">
        <h3 class="text-lg font-medium mb-4">出入库趋势</h3>
        <div ref="chartRef" class="h-72"></div>
      </div>
      
      <!-- 最近操作记录 -->
      <div class="bg-white rounded-xl p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium">最近操作记录</h3>
          <el-button text type="primary" @click="$router.push('/order/records')">
            查看全部
          </el-button>
        </div>
        <el-table :data="recentRecords" stripe size="small">
          <el-table-column prop="material_name" label="物资" min-width="120" />
          <el-table-column label="类型" width="80">
            <template #default="{ row }">
              <el-tag :type="row.operation_type === 1 ? 'success' : 'warning'" size="small">
                {{ row.operation_type === 1 ? '入库' : '出库' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="operator_name" label="操作人" width="80" />
          <el-table-column label="时间" width="140">
            <template #default="{ row }">
              {{ formatTime(row.operation_time) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { House, Box, Upload, Download, DataLine } from '@element-plus/icons-vue'
import { getOverview, getInboundOutboundChart, getRecentRecords } from '@/api/dashboard'

const chartRef = ref()
const statistics = ref([])
const recentRecords = ref([])

const formatTime = (time) => {
  if (!time) return '-'
  return time.replace('T', ' ').slice(0, 16)
}

const initChart = async () => {
  const chart = echarts.init(chartRef.value)
  
  try {
    const res = await getInboundOutboundChart(7)
    const data = res.data || []
    
    chart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['入库', '出库']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.map(d => d.date.slice(5))
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '入库',
          type: 'line',
          smooth: true,
          data: data.map(d => d.inbound),
          itemStyle: { color: '#67c23a' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
            ])
          }
        },
        {
          name: '出库',
          type: 'line',
          smooth: true,
          data: data.map(d => d.outbound),
          itemStyle: { color: '#e6a23c' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
              { offset: 1, color: 'rgba(230, 162, 60, 0.05)' }
            ])
          }
        }
      ]
    })
  } catch (error) {
    console.error(error)
  }
}

const loadData = async () => {
  try {
    const res = await getOverview()
    const data = res.data
    
    statistics.value = [
      {
        title: '库房总数',
        value: data.warehouse?.total || 0,
        icon: House,
        color: 'text-primary',
        bgColor: 'bg-primary/10'
      },
      {
        title: '在库物资',
        value: data.material?.total_types || 0,
        subtitle: `共 ${data.material?.total_quantity || 0} 件`,
        icon: Box,
        color: 'text-green-500',
        bgColor: 'bg-green-50'
      },
      {
        title: '今日入库',
        value: data.today?.inbound || 0,
        icon: Upload,
        color: 'text-blue-500',
        bgColor: 'bg-blue-50'
      },
      {
        title: '今日出库',
        value: data.today?.outbound || 0,
        icon: Download,
        color: 'text-orange-500',
        bgColor: 'bg-orange-50'
      }
    ]
  } catch (error) {
    console.error(error)
  }
}

const loadRecentRecords = async () => {
  try {
    const res = await getRecentRecords(5)
    recentRecords.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadData()
  loadRecentRecords()
  initChart()
})
</script>
