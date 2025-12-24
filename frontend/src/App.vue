<template>
  <div id="app">
    <NavigationBar />
    <router-view />
    <ToastMessage 
      :show="toastStore.show" 
      :message="toastStore.message" 
      :type="toastStore.type" 
      :duration="toastStore.duration"
      @close="toastStore.close"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/stores/toast'
import { useRouter, useRoute } from 'vue-router' // useRoute 추가
import NavigationBar from '@/components/NavigationBar.vue'
import ToastMessage from '@/components/ToastMessage.vue'

const authStore = useAuthStore()
const toastStore = useToastStore()
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
