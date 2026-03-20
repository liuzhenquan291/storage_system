<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

onMounted(() => {
  // 初始化时检查 token
  userStore.initUser()
})
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}
</style>
