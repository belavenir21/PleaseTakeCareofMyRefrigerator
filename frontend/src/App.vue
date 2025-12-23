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
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('No token found, skipping profile fetch')
    return
  }

  try {
    await authStore.fetchUserProfile()
    
    if (authStore.isAuthenticated && route.path === '/') {
      console.log("Auto redirect to Pantry")
      router.replace({ name: 'Pantry' })
    }
  } catch (error) {
    console.error('Initial profile fetch failed:', error)
  }
})
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
}
</style>
