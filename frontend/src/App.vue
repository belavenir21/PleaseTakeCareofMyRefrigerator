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
  try {
    await authStore.fetchUserProfile()
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
