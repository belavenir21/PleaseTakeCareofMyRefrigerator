<template>
  <div id="app">
    <NavigationBar />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useRouter, useRoute } from 'vue-router' // useRoute 추가
import NavigationBar from '@/components/NavigationBar.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

onMounted(async () => {
  try {
    await authStore.fetchUserProfile()
    
    // [새로고침/초기진입 감지]
    // 이미 로그인되어 있고, 현재 경로가 루트('/')라면 보관함으로 이동
    // (단, 로그인 페이지에서 넘어오는 경우는 제외해야 하는데, onMounted는 새로고침 시에만 실행되므로 안전)
    // 주의: SPA 내부 이동시에는 App.vue가 언마운트되지 않으므로 이 코드는 실행되지 않음 -> 의도대로 동작!
    if (authStore.isAuthenticated && route.path === '/') {
      console.log("Auto redirect to Pantry")
      router.replace({ name: 'Pantry' })
    }

  } catch (error) {
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
