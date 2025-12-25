<template>
  <div class="settings-view">
    <header class="header-premium">
      <div class="header-inner">
        <button @click="goBack" class="btn-back-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">프로필 설정</h2>
      </div>
    </header>

    <div class="container">
      <div class="card settings-card">
        <form @submit.prevent="handleSubmit">
          <!-- 프로필 사진 섹션 -->
          <div class="profile-header-edit">
            <div class="avatar-container" @click="triggerImageUpload">
              <div class="avatar" v-if="!previewUrl && !profile?.image_url">👤</div>
              <img :src="previewUrl || profile?.image_url" v-else class="avatar-img" />
              <div class="avatar-edit-overlay">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
              </div>
            </div>
            <div class="avatar-hint">
              <p>사진 변경</p>
            </div>
            <input type="file" ref="fileInput" style="display: none" @change="handleImageChange" accept="image/*" />
          </div>

          <!-- 정보 수정 섹션 -->
          <div class="edit-fields">
            <div class="input-group">
              <label>닉네임 <span class="required">*</span></label>
              <input
                v-model="inputNickname"
                type="text"
                class="input-field"
                placeholder="닉네임을 입력하세요"
                required
              />
            </div>

            <div class="input-group">
              <label>식단 목표</label>
              <div class="tag-input-container" @click="focusTagInput">
                <span v-for="(tag, index) in tags" :key="index" class="tag-bubble">
                  {{ tag }}
                  <button type="button" @click.stop="removeTag(index)" class="btn-remove-tag">×</button>
                </span>
                <input
                  ref="tagInputRef"
                  v-model="tagInput"
                  type="text"
                  class="tag-input-field"
                  placeholder="#다이어트 #비건 (엔터)"
                  @keydown.enter.prevent="addTag"
                  @keydown.backspace="handleBackspace"
                />
              </div>
              <p class="helper-text">💡 예: 다이어트, 저염식, 채식, 글루텐프리 등</p>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '저장 중...' : '저장하기' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 계정 관련 (하단 배치) -->
      <div class="account-actions">
        <button class="text-btn" @click="handlePasswordChange">비밀번호 변경</button>
        <span class="divider">|</span>
        <button class="text-btn danger" @click="handleDeleteAccount">회원 탈퇴</button>
      </div>

      <p class="info-text">
        현재 앱 버전: 1.0.1
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()

const loading = ref(false)
const profile = computed(() => authStore.profile)

// Form Data
const inputNickname = ref('')
const tags = ref([])
const tagInput = ref('')
const selectedImageFile = ref(null)
const previewUrl = ref(null)

// Refs
const tagInputRef = ref(null)
const fileInput = ref(null)

onMounted(() => {
  if (profile.value) {
    inputNickname.value = profile.value.nickname || ''
    if (profile.value.diet_goals) {
      tags.value = profile.value.diet_goals.split(' ').filter(t => t.startsWith('#'))
    }
  }
})

// Tags Logic
const focusTagInput = () => tagInputRef.value.focus()

const addTag = () => {
  const val = tagInput.value.trim()
  if (!val) return
  const newTag = val.startsWith('#') ? val : `#${val}`
  if (!tags.value.includes(newTag)) tags.value.push(newTag)
  tagInput.value = ''
}

const removeTag = (index) => tags.value.splice(index, 1)

const handleBackspace = () => {
  if (tagInput.value === '' && tags.value.length > 0) {
    tags.value.pop()
  }
}

// Image Logic
const triggerImageUpload = () => fileInput.value.click()

const handleImageChange = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Preview
  selectedImageFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

// Submit Logic
const handleSubmit = async () => {
  if (!inputNickname.value || inputNickname.value.trim() === '') {
    toast.warning('닉네임은 필수입니다.')
    return
  }

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('nickname', inputNickname.value)
    formData.append('diet_goals', tags.value.join(' '))
    
    if (selectedImageFile.value) {
      formData.append('profile_image', selectedImageFile.value) // Django Serializer 필드명
    }

    await authStore.updateProfile(formData)
    toast.success('프로필이 성공적으로 저장되었습니다!')
    
    // 뒤로가기? or Stay
    // router.push({ name: 'Profile' }) 
  } catch (error) {
    console.error('Update failed:', error)
    if (error.response?.data?.error) {
       toast.error(error.response.data.error)
    } else {
       toast.error('프로필 수정 실패. 다시 시도해주세요.')
    }
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    router.push({ name: 'Profile' })
  }
}

const handlePasswordChange = () => toast.info('비밀번호 변경 기능은 준비 중입니다.')

const handleDeleteAccount = () => {
  if (confirm('정말로 탈퇴하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
    toast.warning('탈퇴 처리 기능은 준비 중입니다.')
  }
}
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  background: var(--bg-main);
  padding-top: 70px;
}

.container {
  max-width: 500px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-card {
  background: white;
  border-radius: 20px;
  padding: 30px 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}

/* Profile Header (Image) */
.profile-header-edit {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 30px;
}

.avatar-container {
  position: relative;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  overflow: hidden;
  background: #f1f3f5;
  cursor: pointer;
  border: 4px solid white;
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s;
}

.avatar-container:hover { transform: scale(1.05); }

.avatar { font-size: 3.5rem; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.avatar-edit-overlay {
  position: absolute; bottom: 0; left: 0; right: 0; height: 35%;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  color: white; opacity: 0; transition: opacity 0.2s;
}
.avatar-container:hover .avatar-edit-overlay { opacity: 1; }

.avatar-hint {
  font-size: 0.9rem;
  color: #868e96;
  font-weight: 500;
}

/* Input Fields */
.edit-fields {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 700;
  color: var(--text-dark);
  font-size: 0.95rem;
}

.required { color: #fa5252; }

.input-field {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary);
}

/* Tag Input */
.tag-input-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 10px;
  min-height: 50px;
  cursor: text;
}
.tag-input-container:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.1);
}

.tag-bubble {
  background: #FFF0F5; color: #FF69B4;
  padding: 6px 12px; border-radius: 20px;
  font-size: 0.9rem; font-weight: 700;
  display: flex; align-items: center; gap: 6px;
  border: 1px solid rgba(255, 105, 180, 0.2);
}

.btn-remove-tag {
  background: none; border: none; color: #FF69B4;
  font-size: 1.1rem; cursor: pointer; padding: 0; line-height: 1;
  display: flex; align-items: center;
}

.tag-input-field {
  border: none; outline: none; font-size: 0.95rem;
  flex: 1; min-width: 120px; background: transparent; padding: 4px;
}

.helper-text {
  margin-top: 6px;
  font-size: 0.85rem;
  color: #adb5bd;
}

/* Actions */
.form-actions { margin-top: 30px; }

.btn-primary {
  width: 100%;
  padding: 16px;
  font-size: 1.1rem;
  border-radius: 14px;
  font-weight: 800;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

.account-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

.divider { color: #dee2e6; }

.text-btn {
  background: none; border: none;
  font-size: 0.9rem; color: #868e96;
  cursor: pointer; text-decoration: underline;
}

.text-btn.danger { color: #ff6b6b; }

.info-text {
  text-align: center; font-size: 0.8rem; color: #ced4da; margin-top: 20px;
}
</style>
