<template>
  <div class="settings-view">
    <header class="header-premium">
      <div class="header-inner">
        <button @click="goBack" class="btn-back-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">계정 설정</h2>
      </div>
    </header>

    <div class="container">
      <div class="card settings-card">
        <h3>🔒 보안 설정</h3>
        <div class="setting-item">
          <div class="setting-info">
            <span class="label">비밀번호 변경</span>
            <p class="desc">주기적인 비밀번호 변경으로 계정을 보호하세요.</p>
          </div>
          <button class="btn-action" @click="handlePasswordChange">변경</button>
        </div>
      </div>

      <!-- 회원 탈퇴 버튼 (독립 섹션) -->
      <div class="delete-account-section">
        <button class="btn-delete-account" @click="handleDeleteAccount">
          <span class="icon">⚠️</span>
          <div class="text">
            <span class="title">회원 탈퇴</span>
            <span class="subtitle">계정과 모든 데이터가 영구 삭제됩니다</span>
          </div>
        </button>
      </div>
      
      <p class="info-text">
        현재 앱 버전: 1.0.0
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const toast = useToastStore()

const goBack = () => {
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    // 설정 페이지에서는 프로필 페이지로 가는 것이 자연스러움
    router.push({ name: 'Profile' })
  }
}

const handlePasswordChange = () => {
  toast.info('비밀번호 변경 기능은 준비 중입니다.')
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
}


.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.settings-card h3 {
  margin: 0 0 16px;
  font-size: 1rem;
  color: #adb5bd;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.setting-info {
  flex: 1;
  margin-right: 16px;
}

.label {
  display: block;
  font-weight: 700;
  font-size: 1rem;
  color: #333;
  margin-bottom: 4px;
}

.desc {
  font-size: 0.85rem;
  color: #868e96;
  margin: 0;
  line-height: 1.4;
}

.text-danger {
  color: #ff6b6b;
}

.btn-action {
  background: #f1f3f5;
  color: #495057;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.btn-action:hover {
  background: #e9ecef;
}

.btn-danger {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: #fa5252;
}

/* 회원 탈퇴 독립 섹션 */
.delete-account-section {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px dashed #ffe3e3;
}

.btn-delete-account {
  width: 100%;
  background: #fff5f5;
  border: 2px solid #ffe3e3;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.btn-delete-account:hover {
  background: #ffe3e3;
  border-color: #ff6b6b;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 107, 107, 0.15);
}

.btn-delete-account .icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.btn-delete-account .text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.btn-delete-account .title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #ff6b6b;
}

.btn-delete-account .subtitle {
  font-size: 0.85rem;
  color: #868e96;
}

.info-text {
  text-align: center;
  font-size: 0.8rem;
  color: #adb5bd;
  margin-top: 20px;
}
</style>
