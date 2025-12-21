<template>
  <div class="chat-modal-overlay" @click.self="$emit('close')">
    <div class="chat-modal">
      <div class="chat-header">
        <div class="header-info">
          <span class="chef-icon">👨‍🍳</span>
          <div>
            <h3>AI 레시피 셰프</h3>
            <p class="subtitle">무엇이든 물어보세요!</p>
          </div>
        </div>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <div class="chat-body" ref="chatBody">
        <!-- 빠른 질문 버튼 -->
        <div v-if="messages.length === 0" class="welcome-section">
          <div class="welcome-icon">🍳</div>
          <h4>AI 셰프가 도와드릴게요!</h4>
          <p>내 냉장고 재료로 만들 수 있는<br/>요리를 추천해드려요.</p>
        </div>

        <!-- 메시지 목록 -->
        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
          <div class="message-content" v-html="formatMessage(msg.content)"></div>
        </div>

        <!-- 로딩 -->
        <div v-if="loading" class="message assistant">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>

        <!-- 빠른 질문 (메시지 있을 때도 표시) -->
        <div v-if="!loading && availableQuickActions.length > 0" class="quick-actions">
          <button 
            v-for="action in availableQuickActions" 
            :key="action.id"
            @click="sendQuickMessage(action)"
            class="quick-btn"
          >
            {{ action.icon }} {{ action.label }}
          </button>
        </div>
      </div>

      <div class="chat-footer">
        <div class="input-wrap">
          <input 
            v-model="userInput"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="레시피에 대해 물어보세요..."
            :disabled="loading"
          />
          <button @click="sendMessage" :disabled="loading || !userInput.trim()" class="btn-send">
            →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import { recipeAPI } from '@/api/recipe'

const emit = defineEmits(['close'])

const messages = ref([])
const userInput = ref('')
const loading = ref(false)
const chatBody = ref(null)
const usedActionIds = ref(new Set())

const quickActions = [
  { id: 'myingredients', icon: '🧊', label: '내 재료로 요리 추천', message: '내 냉장고 재료로 만들 수 있는 요리 추천해줘', includeIngredients: true },
  { id: 'simple', icon: '⚡', label: '간단 레시피', message: '간단하고 빠른 요리 알려줘', includeIngredients: true },
  { id: 'diet', icon: '🥗', label: '다이어트 요리', message: '다이어트에 좋은 레시피 추천해줘', includeIngredients: true },
]

const availableQuickActions = computed(() => 
  quickActions.filter(a => !usedActionIds.value.has(a.id))
)

const formatMessage = (text) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatBody.value) {
    chatBody.value.scrollTop = chatBody.value.scrollHeight
  }
}

const sendQuickMessage = (action) => {
  usedActionIds.value.add(action.id)
  userInput.value = action.message
  sendMessageWithIngredients(action.includeIngredients)
}

const sendMessage = () => {
  sendMessageWithIngredients(true) // 기본적으로 내 재료 포함
}

const sendMessageWithIngredients = async (includeIngredients) => {
  const message = userInput.value.trim()
  if (!message || loading.value) return

  messages.value.push({ role: 'user', content: message })
  userInput.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const response = await recipeAPI.sendChatMessage(message, includeIngredients)
    messages.value.push({ role: 'assistant', content: response.message })
  } catch (error) {
    messages.value.push({ role: 'assistant', content: '죄송합니다, 오류가 발생했습니다. 다시 시도해주세요. 😅' })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.chat-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.chat-modal {
  background: white;
  border-radius: 24px;
  width: 90%;
  max-width: 500px;
  height: 80vh;
  max-height: 700px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 80px rgba(0,0,0,0.3);
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.chef-icon { font-size: 2rem; }
.chat-header h3 { margin: 0; font-size: 1.1rem; }
.subtitle { margin: 0; font-size: 0.8rem; opacity: 0.8; }
.btn-close {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

.welcome-section {
  text-align: center;
  padding: 30px 20px;
}
.welcome-icon { font-size: 4rem; margin-bottom: 15px; }
.welcome-section h4 { margin: 0 0 10px; font-size: 1.2rem; color: #333; }
.welcome-section p { color: #666; font-size: 0.9rem; line-height: 1.5; }

.message { margin-bottom: 16px; }
.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-left: 60px;
  border-radius: 18px 18px 4px 18px;
  padding: 14px 18px;
}
.message.assistant .message-content {
  background: white;
  color: #333;
  margin-right: 60px;
  border-radius: 18px 18px 18px 4px;
  border: 1px solid #e9ecef;
  padding: 14px 18px;
  line-height: 1.6;
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 14px 18px;
  background: white;
  border-radius: 18px;
  width: fit-content;
  border: 1px solid #e9ecef;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #adb5bd;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}
.quick-btn {
  background: white;
  border: 1px solid #e9ecef;
  padding: 10px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.quick-btn:hover {
  background: #e7f5ff;
  border-color: #74c0fc;
}

.chat-footer {
  padding: 16px;
  background: white;
  border-top: 1px solid #e9ecef;
}
.input-wrap {
  display: flex;
  gap: 10px;
}
.input-wrap input {
  flex: 1;
  border: 1px solid #e9ecef;
  padding: 14px 18px;
  border-radius: 25px;
  font-size: 0.95rem;
  outline: none;
}
.input-wrap input:focus { border-color: #667eea; }
.btn-send {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  font-size: 1.3rem;
  cursor: pointer;
}
.btn-send:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
