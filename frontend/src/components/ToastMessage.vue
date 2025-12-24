<template>
  <Teleport to="body">
    <Transition name="toast-slide">
      <div v-if="show" class="toast-container" :class="`toast-${type}`">
        <div class="toast-icon">{{ icon }}</div>
        <div class="toast-content">
          <p class="toast-message">{{ message }}</p>
        </div>
        <button @click="close" class="toast-close">×</button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  message: String,
  type: {
    type: String,
    default: 'info', // info, success, warning, error
    validator: (val) => ['info', 'success', 'warning', 'error'].includes(val)
  },
  duration: {
    type: Number,
    default: 3000
  },
  show: Boolean
})

const emit = defineEmits(['close'])

const icon = ref('ℹ️')
const iconMap = {
  info: 'ℹ️',
  success: '✅',
  warning: '⚠️',
  error: '❌'
}

watch(() => props.type, (newType) => {
  icon.value = iconMap[newType] || iconMap.info
}, { immediate: true })

watch(() => props.show, (newShow) => {
  if (newShow && props.duration > 0) {
    setTimeout(() => {
      close()
    }, props.duration)
  }
})

const close = () => {
  emit('close')
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  right: 24px;
  z-index: 99999;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 300px;
  max-width: 400px;
  padding: 16px 20px;
  border-radius: 16px;
  background: white;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border: 2px solid;
  animation: bounce-in 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes bounce-in {
  0% {
    transform: translateY(-100px) scale(0.8);
    opacity: 0;
  }
  50% {
    transform: translateY(10px) scale(1.05);
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

/* Type-specific styles */
.toast-info {
  border-color: #74C0FC;
  background: linear-gradient(135deg, #E7F5FF 0%, #D0EBFF 100%);
}

.toast-success {
  border-color: #8CE99A;
  background: linear-gradient(135deg, #EBFBEE 0%, #D3F9D8 100%);
}

.toast-warning {
  border-color: #FFD43B;
  background: linear-gradient(135deg, #FFF9DB 0%, #FFF3BF 100%);
}

.toast-error {
  border-color: #FF8787;
  background: linear-gradient(135deg, #FFE3E3 0%, #FFC9C9 100%);
}

.toast-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  animation: wiggle 0.5s ease-in-out;
}

@keyframes wiggle {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

.toast-content {
  flex: 1;
}

.toast-message {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #868e96;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
  flex-shrink: 0;
}

.toast-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #495057;
  transform: rotate(90deg);
}

/* Transition */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s ease;
}

.toast-slide-enter-from {
  transform: translateX(400px);
  opacity: 0;
}

.toast-slide-leave-to {
  transform: translateX(400px);
  opacity: 0;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .toast-container {
    right: 16px;
    left: 16px;
    min-width: unset;
    max-width: unset;
  }
}
</style>
