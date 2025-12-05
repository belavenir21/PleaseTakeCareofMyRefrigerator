<template>
  <div id="app">
    <NavigationBar />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import NavigationBar from '@/components/NavigationBar.vue'

const authStore = useAuthStore()

onMounted(async () => {
  // 페이지 로드 시 사용자 정보 확인
  try {
    await authStore.fetchUserProfile()
  } catch (error) {
    // 로그인하지 않은 상태
    console.log('Not authenticated')
  }
})
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
}
</style>
