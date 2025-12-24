import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
    const show = ref(false)
    const message = ref('')
    const type = ref('info')
    const duration = ref(3000)

    const showToast = ({ message: msg, type: toastType = 'info', duration: dur = 3000 }) => {
        message.value = msg
        type.value = toastType
        duration.value = dur
        show.value = true
    }

    const close = () => {
        show.value = false
    }

    // Helper methods
    const success = (msg, dur = 3000) => showToast({ message: msg, type: 'success', duration: dur })
    const error = (msg, dur = 3000) => showToast({ message: msg, type: 'error', duration: dur })
    const warning = (msg, dur = 3000) => showToast({ message: msg, type: 'warning', duration: dur })
    const info = (msg, dur = 3000) => showToast({ message: msg, type: 'info', duration: dur })

    return {
        show,
        message,
        type,
        duration,
        showToast,
        close,
        success,
        error,
        warning,
        info
    }
})
