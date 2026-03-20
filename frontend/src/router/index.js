import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/layout/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'DataLine' }
      },
      {
        path: 'user',
        name: 'User',
        component: () => import('@/views/user/index.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'role',
        name: 'Role',
        component: () => import('@/views/role/index.vue'),
        meta: { title: '角色管理', icon: 'UserFilled' }
      },
      {
        path: 'warehouse',
        name: 'Warehouse',
        redirect: '/warehouse/info',
        meta: { title: '库房管理', icon: 'House' },
        children: [
          {
            path: 'info',
            name: 'WarehouseInfo',
            component: () => import('@/views/warehouse/info.vue'),
            meta: { title: '库房管理' }
          },
          {
            path: 'line',
            name: 'ProductionLine',
            component: () => import('@/views/warehouse/line.vue'),
            meta: { title: '产线管理' }
          },
          {
            path: 'shelf',
            name: 'Shelf',
            component: () => import('@/views/warehouse/shelf.vue'),
            meta: { title: '货架管理' }
          },
          {
            path: 'location',
            name: 'Location',
            component: () => import('@/views/warehouse/location.vue'),
            meta: { title: '库位管理' }
          }
        ]
      },
      {
        path: 'material',
        name: 'Material',
        redirect: '/material/type',
        meta: { title: '物资管理', icon: 'Box' },
        children: [
          {
            path: 'type',
            name: 'MaterialType',
            component: () => import('@/views/material/type.vue'),
            meta: { title: '物资类型' }
          },
          {
            path: 'stock',
            name: 'MaterialStock',
            component: () => import('@/views/material/stock.vue'),
            meta: { title: '在库物资' }
          },
          {
            path: 'outbound',
            name: 'OutboundRecord',
            component: () => import('@/views/material/outbound.vue'),
            meta: { title: '出库记录' }
          }
        ]
      },
      {
        path: 'order',
        name: 'Order',
        redirect: '/order/inbound',
        meta: { title: '工单管理', icon: 'Document' },
        children: [
          {
            path: 'inbound',
            name: 'InboundOrder',
            component: () => import('@/views/order/inbound.vue'),
            meta: { title: '入库任务' }
          },
          {
            path: 'outbound',
            name: 'OutboundOrder',
            component: () => import('@/views/order/outbound.vue'),
            meta: { title: '出库任务' }
          },
          {
            path: 'stocktake',
            name: 'StocktakeOrder',
            component: () => import('@/views/order/stocktake.vue'),
            meta: { title: '盘点任务' }
          },
          {
            path: 'records',
            name: 'OrderRecords',
            component: () => import('@/views/order/records.vue'),
            meta: { title: '出入库记录' }
          }
        ]
      },
      {
        path: 'device',
        name: 'Device',
        redirect: '/device/info',
        meta: { title: '设备管理', icon: 'Monitor' },
        children: [
          {
            path: 'info',
            name: 'DeviceInfo',
            component: () => import('@/views/device/info.vue'),
            meta: { title: '设备信息' }
          },
          {
            path: 'iot',
            name: 'IotDevice',
            component: () => import('@/views/device/iot.vue'),
            meta: { title: 'IOT设备' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth !== false && !userStore.token) {
    next('/login')
  } else if (to.path === '/login' && userStore.token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
