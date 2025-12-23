# 🧹 프로젝트 정리 체크리스트

## ❌ 삭제해도 되는 파일들

### 루트 디렉토리
- [ ] `ORIGINAL_README.txt` - 원본 README, 이제 불필요
- [ ] `PROJECT_STRUCTURE.md` - 프로젝트 구조 문서, 현재 사용 안 함
- [ ] `REMAINING_TASKS.md` - 남은 작업 목록, 완료됨
- [ ] `TODO_MANUAL_EDITS.md` - 수동 편집 TODO, 완료됨
- [ ] `RULES.md` - 규칙 파일, 내용 거의 없음

### Backend 루트 디렉토리 (스크립트 파일들)
**아이콘 관련 스크립트 (개발 완료, 삭제 가능):**
- [ ] `fix_icons.py`
- [ ] `fix_icons_detailed.py`
- [ ] `fix_icons_final.py`
- [ ] `correct_icon_priority.py`
- [ ] `final_icon_sync.py`
- [ ] `fix_drink_icons.py`
- [ ] `smart_icon_sync.py`
- [ ] `split_additional_icons.py`
- [ ] `split_icons.py`
- [ ] `split_icons_pillow.py`
- [ ] `sync_icons_db.py`
- [ ] `update_icons_db.py`
- [ ] `update_icons_final.py`
- [ ] `update_icons_priority.py`
- [ ] `upscale_icons.py`
- [ ] `verify_icon_coverage.py`

**숙주 관련 스크립트 (버그 수정 완료, 삭제 가능):**
- [ ] `fix_sprouts.py`
- [ ] `consolidate_sprouts.py`
- [ ] `fix_sukju_db.py`
- [ ] `fix_sukju_final.py`
- [ ] `fix_sukju_icon.py`
- [ ] `fix_sukju_icon.sql`
- [ ] `fix_sukju_icon_final.py`
- [ ] `fix_sukju_image.sql`
- [ ] `fix_sukju_shell.py`

**기타 개발용 스크립트 (삭제 가능):**
- [ ] `cleanup_ingredients.py`
- [ ] `fix_pumpkin.py`
- [ ] `fix_line.py`
- [ ] `fix_missing_nicknames.py`
- [ ] `quick_fix_nicknames.py`
- [ ] `heal_user_ings.py`
- [ ] `link_historical_ingredients.py`
- [ ] `seed_ingredients.py`
- [ ] `test_huggingface.py`
- [ ] `verify_test.py`

**데이터 체크 파일 (삭제 가능):**
- [ ] `check_final_data.py`
- [ ] `check_img_info.py`
- [ ] `check_recipe.json`
- [ ] `data_check_summary.json`
- [ ] `find_table.py`

**백업 및 로그 파일 (보관 또는 삭제):**
- [ ] `master_backup.json` - 373KB, 백업용
- [ ] `recipe_ingredients_backup.json` - 119KB, 백업용
- [ ] `master_names.txt`
- [ ] `icon_mapping_log.txt`
- [ ] `final_icon_update_log.txt`
- [ ] `ingredient_debug.json`
- [ ] `no_images.json`
- [ ] `verification_result.json`

**레시피 재료 수정 스크립트 (완료, 삭제 가능):**
- [ ] `fix_recipe_ingredients.py`
- [ ] `fix_recipe_ingredients_batch.py`

**Dump 스크립트 (필요시):**
- [ ] `dump_masters.py`

### Backend Management Commands
**유지해야 할 명령어:**
- ✅ `accounts/management/commands/create_default_user.py` - 기본 사용자 생성
- ✅ `recipes/management/commands/fetch_recipes.py` - 레시피 가져오기
- ✅ `recipes/management/commands/load_initial_data.py` - 초기 데이터 로드
- ✅ `recipes/management/commands/check_yushi_recipes.py` - 유저 레시피 확인

**삭제 가능한 명령어:**
- [ ] `accounts/management/commands/fix_nicknames.py` - 닉네임 수정 완료
- [ ] `recipes/management/commands/clean_recipe_ingredients.py` - 재료 정리 완료
- [ ] `recipes/management/commands/extract_ingredients.py` - 재료 추출 완료
- [ ] `recipes/management/commands/rebuild_recipe_ingredients_ai.py` - AI 재구성 완료
- [ ] `recipes/management/commands/export_fixtures.py` - fixture 추출용
- [ ] `recipes/management/commands/init_simple_recipes.py` - 초기화 완료

## ⚠️ 확인 필요

### Backend
- [ ] `backend/data/` - 초기 데이터 디렉토리, 내용 확인 필요
- [ ] `backend/fixtures/` - fixture 파일들, 필요시 유지
- [ ] `backend/media/` - 업로드된 미디어 파일들

### Frontend
- 확인 필요 없음, 빌드 시 자동 처리

## ✅ 유지해야 할 파일

### 루트
- ✅ `README.md` - 메인 문서
- ✅ `RAILWAY_DEPLOY_GUIDE.md` - 배포 가이드
- ✅ `SOCIAL_AUTH_SETUP.md` - 소셜 인증 설정

### Backend
- ✅ `.env` - 환경 변수 (보안 주의!)
- ✅ `.env.example` - 환경 변수 예시
- ✅ `Procfile` - Railway 배포용
- ✅ `runtime.txt` - Python 버전
- ✅ `requirements.txt` - 패키지 목록
- ✅ `manage.py` - Django 관리
- ✅ `db.sqlite3` - 데이터베이스

### Frontend
- 모든 소스 파일 유지

## 📝 권장 정리 순서

1. **1단계: 백업**
   ```bash
   # 전체 프로젝트 백업
   cp -r backend backend_backup
   ```

2. **2단계: 스크립트 파일 삭제**
   - 아이콘 관련 (15개)
   - 숙주 관련 (9개)
   - 기타 개발용 (15개)

3. **3단계: 로그/백업 파일 정리**
   - 백업 JSON 파일 → 별도 저장 후 삭제
   - 로그 TXT 파일 삭제

4. **4단계: Management Commands 정리**
   - 완료된 스크립트 6개 삭제

## 💾 총 절약 공간

- 스크립트 파일: ~50개 (약 150KB)
- 백업 파일: 2개 (약 500KB)
- 로그 파일: 6개 (약 20KB)

**총 예상 절약**: 약 670KB + 정리된 구조
