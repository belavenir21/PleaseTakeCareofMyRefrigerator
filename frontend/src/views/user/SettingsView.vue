<template>
  <div class="settings-view">
    <header class="header">
      <button @click="goBack" class="btn-back">←</button>
      <h2>계정 설정</h2>
      <div style="width: 24px"></div>
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

      <div class="card settings-card danger-zone">
        <h3>⚠️ 위험 구역</h3>
        <div class="setting-item">
          <div class="setting-info">
            <span class="label text-danger">회원 탈퇴</span>
            <p class="desc">계정과 모든 데이터를 삭제합니다. 이 작업은 되돌릴 수 없습니다.</p>
          </div>
          <button class="btn-danger" @click="handleDeleteAccount">탈퇴</button>
        </div>
      </div>
      
      <p class="info-text">
        현재 앱 버전: 1.0.0
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    // 설정 페이지에서는 프로필 페이지로 가는 것이 자연스러움
    router.push({ name: 'Profile' })
  }
}

const handlePasswordChange = () => {
  alert('비밀번호 변경 기능은 준비 중입니다.')
}

const handleDeleteAccount = () => {
  if (confirm('정말로 탈퇴하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
    alert('탈퇴 처리가 완료되지 않았습니다. (준비 중)')
  }
}
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  background: var(--bg-main);
  padding-top: 70px;
}

.header {
  background: white;
  padding: 12px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 70px;
  z-index: 100;
}

.header h2 {
  font-size: 1.1rem;
  font-weight: 800;
  margin: 0;
}

.btn-back {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
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

.danger-zone {
  border: 1px solid #ffe3e3;
}

.info-text {
  text-align: center;
  font-size: 0.8rem;
  color: #adb5bd;
  margin-top: 20px;
}
</style>
