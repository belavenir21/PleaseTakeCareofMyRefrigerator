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
      <!-- 프로필 설정 카드 -->
      <div class="card settings-card">
        <form @submit.prevent="handleSubmit">
          <h3 class="card-title">기본 정보</h3>
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
                <label>아이디</label>
                <input
                  type="text"
                  class="input-field"
                  :value="user?.username"
                  disabled
                  readonly
                  style="background-color: #f8f9fa; color: #868e96;"
                />
            </div>

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
              {{ loading ? '저장 중...' : '프로필 저장' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 비밀번호 변경 카드 (Toggle 방식) -->
      <div v-if="showPasswordChange" class="card settings-card slide-down">
        <h3 class="card-title">비밀번호 변경</h3>
        <form @submit.prevent="handlePasswordUpdate">
            <div class="input-group">
                <label>현재 비밀번호</label>
                <input type="password" v-model="pwData.old_password" class="input-field" placeholder="현재 비밀번호 (필수)" required />
            </div>
            <div class="input-group" style="margin-top: 15px;">
                <label>새 비밀번호</label>
                <input type="password" v-model="pwData.new_password1" class="input-field" placeholder="새 비밀번호 (8자 이상)" required minlength="8" />
            </div>
            <div class="input-group" style="margin-top: 15px;">
                <label>새 비밀번호 확인</label>
                <input type="password" v-model="pwData.new_password2" class="input-field" placeholder="새 비밀번호 확인" required minlength="8" />
            </div>
            <button type="submit" class="btn btn-secondary" style="margin-top: 20px;" :disabled="pwLoading">
                {{ pwLoading ? '변경 중...' : '비밀번호 변경' }}
            </button>
        </form>
      </div>

      <!-- 계정 관련 (하단 배치) -->
      <div class="account-actions">
        <button class="text-btn" @click="togglePasswordChange">
           {{ showPasswordChange ? '비밀번호 변경 닫기' : '비밀번호 변경' }}
        </button>
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
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()

const loading = ref(false)
const profile = computed(() => authStore.profile)
const user = computed(() => authStore.user)

// Form Data - Profile
const inputNickname = ref('')
const tags = ref([])
const tagInput = ref('')
const selectedImageFile = ref(null)
const previewUrl = ref(null)

// Form Data - Password
const showPasswordChange = ref(false)
const pwLoading = ref(false)
const pwData = reactive({
    old_password: '',
    new_password1: '',
    new_password2: ''
})

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

// Submit Logic - Profile
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
      formData.append('profile_image', selectedImageFile.value)
    }

    await authStore.updateProfile(formData)
    
    // 프로필 새로고침 (업로드한 이미지 반영)
    await authStore.fetchUserProfile()
    
    // ❌ Preview 초기화 제거 - 서버 이미지 로드될 때까지 preview 유지
    // previewUrl.value = null
    // selectedImageFile.value = null
    
    toast.success('프로필이 성공적으로 저장되었습니다!')
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

// Password Logic
const togglePasswordChange = () => {
    showPasswordChange.value = !showPasswordChange.value
    // 접을 때 초기화 안 함 (입력 중일 수 있으니)
}

const handlePasswordUpdate = async () => {
    if (pwData.new_password1 !== pwData.new_password2) {
        toast.error('새 비밀번호가 일치하지 않습니다.')
        return
    }
    
    pwLoading.value = true
    try {
        await authStore.changePassword(pwData)
        toast.success('비밀번호가 변경되었습니다!')
        
        // 입력 초기화 및 닫기
        pwData.old_password = ''
        pwData.new_password1 = ''
        pwData.new_password2 = ''
        showPasswordChange.value = false
        
    } catch (error) {
        console.error('PW Change failed:', error)
        const errData = error.response?.data
        if (errData?.old_password) {
            toast.error('현재 비밀번호가 일치하지 않습니다.')
        } else if (errData?.new_password1) {
            toast.error(`새 비밀번호 오류: ${errData.new_password1[0]}`)
        } else {
            toast.error(errData?.error || '비밀번호 변경에 실패했습니다.')
        }
    } finally {
        pwLoading.value = false
    }
}

const goBack = () => {
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    router.push({ name: 'Main' })
  }
}

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

.slide-down {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.card-title {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--text-dark);
    margin-bottom: 20px;
    border-bottom: 2px solid #f1f3f5;
    padding-bottom: 10px;
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
  background: var(--primary); color: white; border: none; cursor: pointer;
}

.btn-secondary {
  width: 100%;
  padding: 16px;
  font-size: 1.1rem;
  border-radius: 14px;
  font-weight: 800;
  background: #f8f9fa; color: #495057; border: 1px solid #dee2e6; cursor: pointer;
}
.btn-secondary:hover { background: #e9ecef; }

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
