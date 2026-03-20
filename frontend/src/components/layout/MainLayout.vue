<template>
  <div class="min-h-screen bg-background">
    <!-- 侧边栏 - 固定定位，独立滚动 -->
    <aside 
      :class="[
        'fixed left-0 top-0 h-screen bg-white shadow-lg transition-all duration-300 flex flex-col z-50',
        collapsed ? 'w-16' : 'w-56'
      ]"
    >
      <!-- Logo -->
      <div class="h-14 flex items-center justify-center border-b border-gray-100 flex-shrink-0">
        <el-icon v-if="collapsed" :size="24" class="text-primary"><Box /></el-icon>
        <template v-else>
          <el-icon :size="24" class="text-primary mr-2"><Box /></el-icon>
          <span class="font-semibold text-gray-800 whitespace-nowrap">仓储管理</span>
        </template>
      </div>
      
      <!-- 菜单 - 独立滚动区域 -->
      <div class="flex-1 overflow-y-auto overflow-x-hidden">
        <el-menu
          :default-active="activeMenu"
          :collapse="collapsed"
          :collapse-transition="false"
          class="border-none"
          router
        >
          <template v-for="menu in menuList" :key="menu.path">
            <el-sub-menu v-if="menu.children" :index="menu.path">
              <template #title>
                <el-icon><component :is="menu.meta?.icon" /></el-icon>
                <span>{{ menu.meta?.title }}</span>
              </template>
              <el-menu-item 
                v-for="child in menu.children" 
                :key="child.path"
                :index="menu.path + '/' + child.path"
              >
                {{ child.meta?.title }}
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="menu.path">
              <el-icon><component :is="menu.meta?.icon" /></el-icon>
              <span>{{ menu.meta?.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </div>
    </aside>
    
    <!-- 主内容区 - 根据侧边栏宽度调整左边距 -->
    <div 
      :class="[
        'flex flex-col min-h-screen transition-all duration-300',
        collapsed ? 'ml-16' : 'ml-56'
      ]"
    >
      <!-- 顶部导航 - 固定定位 -->
      <header class="sticky top-0 z-40 h-14 bg-white shadow-sm flex items-center justify-between px-4">
        <div class="flex items-center">
          <el-button 
            text 
            :icon="collapsed ? Expand : Fold"
            @click="collapsed = !collapsed"
          />
          <el-breadcrumb separator="/" class="ml-4">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              {{ item.meta?.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="flex items-center">
          <el-dropdown trigger="click">
            <div class="flex items-center cursor-pointer hover:text-primary">
              <el-avatar :size="32" class="bg-primary">
                {{ userStore.userInfo?.real_name?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="ml-2">{{ userStore.userInfo?.real_name }}</span>
              <el-icon class="ml-1"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- 内容区域 -->
      <main class="flex-1 p-4">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Box, Expand, Fold, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const collapsed = ref(false)

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta?.title && item.path !== '/')
})

const menuList = [
  { path: '/dashboard', meta: { title: '仪表盘', icon: 'DataLine' } },
  { path: '/user', meta: { title: '用户管理', icon: 'User' } },
  { path: '/role', meta: { title: '角色管理', icon: 'UserFilled' } },
  { 
    path: '/warehouse', 
    meta: { title: '库房管理', icon: 'House' },
    children: [
      { path: 'info', meta: { title: '库房管理' } },
      { path: 'line', meta: { title: '产线管理' } },
      { path: 'shelf', meta: { title: '货架管理' } },
      { path: 'location', meta: { title: '库位管理' } }
    ]
  },
  { 
    path: '/material', 
    meta: { title: '物资管理', icon: 'Box' },
    children: [
      { path: 'type', meta: { title: '物资类型' } },
      { path: 'stock', meta: { title: '在库物资' } },
      { path: 'outbound', meta: { title: '出库记录' } }
    ]
  },
  { 
    path: '/order', 
    meta: { title: '工单管理', icon: 'Document' },
    children: [
      { path: 'inbound', meta: { title: '入库任务' } },
      { path: 'outbound', meta: { title: '出库任务' } },
      { path: 'stocktake', meta: { title: '盘点任务' } },
      { path: 'records', meta: { title: '出入库记录' } }
    ]
  },
  { 
    path: '/device', 
    meta: { title: '设备管理', icon: 'Monitor' },
    children: [
      { path: 'info', meta: { title: '设备信息' } },
      { path: 'iot', meta: { title: 'IOT设备' } }
    ]
  }
]

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
