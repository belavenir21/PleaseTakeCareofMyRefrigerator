import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import vue3GoogleLogin from 'vue3-google-login'
import './assets/styles/main.css'

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(vue3GoogleLogin, {
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || 'YOUR_CLIENT_ID_HERE.apps.googleusercontent.com'
})

app.mount('#app')
