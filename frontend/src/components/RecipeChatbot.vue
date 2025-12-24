<template>
  <div class="recipe-chatbot">
    <!-- 플로팅 버튼 -->
    <button v-if="!isOpen" @click="toggleChat" class="fab-chat">
      <div class="fab-icon-wrap">
        <img src="@/assets/character-head.png" alt="AI" class="fab-char-img" />
      </div>
      <span class="fab-label">AI 셰프 쿠킹 미미</span>
    </button>

    <!-- 채팅창 -->
    <transition name="chat-slide">
      <div v-if="isOpen" class="chat-window">
        <div class="chat-header">
          <div class="header-info">
            <img src="@/assets/character-head.png" alt="AI" class="header-char-img" />
            <div>
              <h3>AI 셰프 쿠킹 미미</h3>
              <p class="subtitle">무엇이든 물어보세요!</p>
            </div>
          </div>
          <button @click="toggleChat" class="btn-close">×</button>
        </div>

        <div class="chat-body" ref="chatBody">
          <!-- 웰컴 메시지 (메시지 없을 때만) -->
          <div v-if="messages.length === 0" class="welcome-section">
            <div class="welcome-icon-wrap">
              <img src="@/assets/character-head.png" alt="AI" class="welcome-char-img" />
            </div>
            <h3>안녕하세요! AI 셰프 쿠킹 미미에요</h3>
            <p>레시피, 요리 팁, 재료 활용법 등<br/>무엇이든 물어보세요!</p>
          </div>

          <!-- 메시지 목록 -->
          <div v-for="(msg, idx) in messages" :key="idx" 
               :class="['message', msg.role]">
            <div class="message-content">
              <span v-html="formatMessage(msg.content)"></span>
              <span v-if="msg.isTyping" class="typing-cursor">|</span>
            </div>
            <span class="message-time">{{ msg.time }}</span>
          </div>

          <!-- 로딩 -->
          <div v-if="loading" class="message assistant loading">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>

          <!-- 빠른 질문 버튼 (항상 표시, 사용한 것 제외) -->
          <div v-if="!loading && availableQuickActions.length > 0" class="quick-actions-inline">
            <p class="quick-label">빠른 질문:</p>
            <div class="quick-btns-row">
              <button 
                v-for="action in availableQuickActions" 
                :key="action.id"
                @click="sendQuickMessage(action.message, action.includeIngredients, action.id)" 
                class="quick-btn-sm"
              >
                {{ action.icon }} {{ action.label }}
              </button>
            </div>
          </div>
        </div>

        <div class="chat-footer">
          <div class="input-row">
            <label class="checkbox-label">
              <input type="checkbox" v-model="useMyIngredients" />
              <span>내 재료 포함</span>
            </label>
            <div class="input-wrap">
              <textarea 
                ref="inputElement"
                v-model="userInput"
                @keydown.enter.exact.prevent="sendMessage"
                @input="autoResize"
                placeholder="레시피에 대해 물어보세요..."
                :disabled="loading"
                rows="1"
                style="resize: none; overflow-y: hidden; min-height: 40px; max-height: 120px; border-radius: 25px; padding: 14px 18px; border: 1px solid #e9ecef; font-size: 0.9rem; font-family: inherit; outline: none; flex: 1;"
              />
              <button @click="sendMessage" :disabled="loading || !userInput.trim()" class="btn-send">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, reactive } from 'vue'
import { recipeAPI } from '@/api/recipe'

const isOpen = ref(false)
const messages = ref([])
const userInput = ref('')
const loading = ref(false)
const useMyIngredients = ref(true)
const chatBody = ref(null)
const inputElement = ref(null)
const usedQuickActionIds = ref(new Set())

// 빠른 질문 목록
const quickActions = [
  { id: 'ingredients', icon: '🧊', label: '내 재료로 추천', message: '내 냉장고 재료로 만들 수 있는 요리 추천해줘', includeIngredients: true },
  { id: 'simple', icon: '⚡', label: '간단 레시피', message: '간단하고 빠른 한끼 레시피 알려줘', includeIngredients: false },
  { id: 'diet', icon: '🥗', label: '다이어트', message: '다이어트에 좋은 저칼로리 레시피 추천해줘', includeIngredients: false },
  { id: 'leftover', icon: '♻️', label: '재료 활용', message: '남은 재료 활용하는 방법 알려줘', includeIngredients: true },
  { id: 'korean', icon: '🍚', label: '한식', message: '맛있는 한식 레시피 추천해줘', includeIngredients: false },
  { id: 'dessert', icon: '🍰', label: '디저트', message: '집에서 만들 수 있는 간단한 디저트 레시피 알려줘', includeIngredients: false },
]

// 사용하지 않은 빠른 질문만 표시
const availableQuickActions = computed(() => {
  return quickActions.filter(a => !usedQuickActionIds.value.has(a.id))
})

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => scrollToBottom())
  }
}

// 입력칸 자동 높이 조절
const autoResize = () => {
  const textarea = inputElement.value
  if (!textarea) return
  
  textarea.style.height = 'auto'
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
}

const formatMessage = (text) => {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
}

const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatBody.value) {
    chatBody.value.scrollTop = chatBody.value.scrollHeight
  }
}

const sendQuickMessage = (message, includeIngredients, actionId = null) => {
  if (actionId) {
    usedQuickActionIds.value.add(actionId)
  }
  useMyIngredients.value = includeIngredients
  userInput.value = message
  sendMessage()
}

const typeMessage = async (fullText) => {
  if (!fullText) return

  const index = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    time: getCurrentTime(),
    isTyping: true
  })
  
  const chars = Array.from(fullText)
  let currentContent = ''
  
  for (let i = 0; i < chars.length; i++) {
    currentContent += chars[i]
    messages.value[index].content = currentContent
    if (i % 3 === 0) scrollToBottom()
    await new Promise(resolve => setTimeout(resolve, 30))
  }
  
  messages.value[index].isTyping = false
  scrollToBottom()
}

const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message || loading.value) return

  // 사용자 메시지 추가
  messages.value.push({
    role: 'user',
    content: message,
    time: getCurrentTime()
  })
  
  userInput.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const response = await recipeAPI.sendChatMessage(message, useMyIngredients.value)
    loading.value = false // 타이핑 시작 전 점 세개 로딩 제거
    await typeMessage(response.message)
  } catch (error) {
    loading.value = false
    messages.value.push({
      role: 'assistant',
      content: '죄송합니다, 오류가 발생했습니다. 다시 시도해주세요. 😅',
      time: getCurrentTime()
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.recipe-chatbot {
  position: fixed;
  bottom: 100px;
  right: 24px;
  z-index: 9999;
}

/* 플로팅 버튼 */
.fab-chat {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #FFB6C1 0%, #FFC1CC 100%); /* Bubblegum Pink */
  color: white;
  border: none;
  padding: 10px 20px; 
  border-radius: 50px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: 0 8px 30px rgba(255, 182, 193, 0.5);
  transition: all 0.3s ease;
}
.fab-chat:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 12px 40px rgba(255, 182, 193, 0.6);
}
.fab-icon-wrap {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.fab-char-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}
.fab-icon {
  font-size: 1.4rem;
}

/* 채팅창 */
.chat-window {
  position: fixed;
  bottom: 100px;
  right: 24px;
  width: 380px;
  max-width: calc(100vw - 48px);
  height: 550px;
  max-height: calc(100vh - 150px);
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  background: linear-gradient(135deg, #FFB6C1 0%, #FFC1CC 100%);
  color: #6D4C41; /* 헤더 텍스트는 브라운으로? 아니면 흰색? 보통 핑크엔 흰색이 낫지만 컨셉상 브라운이면... 일단 흰색 유지 (글자가 작아서) */
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
.header-char-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
  background: white;
  border-radius: 50%;
  padding: 2px;
}
.chat-header h3 {
  margin: 0;
  font-size: 1.1rem;
}
.subtitle {
  margin: 0;
  font-size: 0.8rem;
  opacity: 0.8;
}
.btn-close {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 채팅 본문 */
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
  position: relative; /* 배경 배치를 위해 */
  z-index: 1;
}

/* 졸귀탱 캐릭터 배경 */
.chat-body::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%; /* 적당한 크기 */
  height: 60%;
  background: url('@/assets/character.png') no-repeat center center;
  background-size: contain;
  opacity: 0.15; /* 은은하게 (글자 방해 안 되게) */
  z-index: -1;
  pointer-events: none;
}

.welcome-section {
  text-align: center;
  padding: 30px 20px;
}
.welcome-icon-wrap {
  width: 80px;
  height: 80px;
  margin: 0 auto 15px;
}
.welcome-char-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  animation: bounce 2s infinite;
}
.welcome-section h3 {
  margin: 0 0 10px;
  font-size: 1.2rem;
  color: #6D4C41;
}
.welcome-section p {
  color: #8D6E63;
  font-size: 0.9rem;
  line-height: 1.5;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 25px;
}
.quick-btn {
  background: white;
  border: 1px solid #e9ecef;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}
.quick-btn:hover {
  border-color: #FF8E99;
  background: #FFF0F6;
  transform: translateX(5px);
}

/* 메시지 */
.message {
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
  display: flex;
  flex-direction: column;
}
.message.user {
  align-items: flex-end;
}
.message.assistant {
  align-items: flex-start;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user .message-content {
  background: linear-gradient(135deg, #FFB6C1 0%, #FFC1CC 100%);
  color: white; 
  border-radius: 18px 18px 4px 18px;
  box-shadow: 0 2px 8px rgba(255, 182, 193, 0.3);
  align-self: flex-end; /* 우측 정렬 강제 */
}
.message.assistant .message-content {
  background: white;
  color: #6D4C41;
  border-radius: 18px 18px 18px 4px;
  border: 1px solid #e9ecef;
  align-self: flex-start; /* 좌측 정렬 강제 */
}
.message-content {
  padding: 12px 16px;
  font-size: 0.9rem;
  line-height: 1.5;
  width: auto; /* width: fit-content 대신 auto와 flex-self 조합 */
  max-width: 85%;
  word-break: break-all;
  display: inline-block;
}
.message-time {
  display: block;
  font-size: 0.7rem;
  color: #adb5bd;
  margin-top: 6px;
  text-align: right;
}
.message.assistant .message-time {
  text-align: left;
}

/* 타이핑 인디케이터 */
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

/* 입력 영역 */
.chat-footer {
  padding: 16px;
  background: white;
  border-top: 1px solid #e9ecef;
}
.input-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: #666;
  cursor: pointer;
}
.checkbox-label input {
  accent-color: #FF8E99;
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
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}
.input-wrap input:focus {
  border-color: #FF8E99;
}
.btn-send {
  background: linear-gradient(135deg, #FFB6C1 0%, #FFC1CC 100%);
  color: white;
  border: none;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}
.btn-send:hover:not(:disabled) {
  transform: scale(1.1);
}
.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 애니메이션 */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(30px) scale(0.95);
}

/* 인라인 빠른 버튼 */
.quick-actions-inline {
  margin-top: 16px;
  padding: 12px;
  background: white;
  border-radius: 16px;
  border: 1px solid #e9ecef;
}
.quick-label {
  margin: 0 0 10px;
  font-size: 0.8rem;
  color: #868e96;
  font-weight: 600;
}
.quick-btns-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.quick-btn-sm {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.quick-btn-sm:hover {
  background: #FFF0F6;
  border-color: #FF8E99;
  transform: scale(1.02);
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background-color: currentColor;
  margin-left: 2px;
  animation: blink 1s step-end infinite;
  vertical-align: middle;
}

@keyframes blink {
  from, to { opacity: 1; }
  50% { opacity: 0; }
}
</style>
