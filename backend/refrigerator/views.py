from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as filters
from datetime import date, timedelta, datetime
from django.conf import settings
from django.utils import timezone
import requests
import re
from .models import UserIngredient
from .serializers import (
    UserIngredientSerializer, 
    UserIngredientListSerializer,
    IngredientScanSerializer
)

class UserIngredientFilter(filters.FilterSet):
    """식재료 필터"""
    storage_method = filters.CharFilter(field_name='storage_method')
    expiring_soon = filters.BooleanFilter(method='filter_expiring_soon')
    expired = filters.BooleanFilter(method='filter_expired')
    
    class Meta:
        model = UserIngredient
        fields = ['storage_method']
    
    def filter_expiring_soon(self, queryset, name, value):
        if value:
            soon_date = date.today() + timedelta(days=3)
            return queryset.filter(expiry_date__lte=soon_date, expiry_date__gte=date.today())
        return queryset
    
    def filter_expired(self, queryset, name, value):
        if value:
            return queryset.filter(expiry_date__lt=date.today())
        return queryset

class UserIngredientViewSet(viewsets.ModelViewSet):
    """사용자 식재료 관리 ViewSet"""
    serializer_class = UserIngredientSerializer
    filterset_class = UserIngredientFilter
    search_fields = ['name']
    ordering_fields = ['expiry_date', 'name', 'created_at']
    ordering = ['expiry_date']

    from config.authentication import CsrfExemptSessionAuthentication
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 기본 쿼리셋은 삭제되지 않은 항목만
        return UserIngredient.objects.filter(user=self.request.user, is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        """Soft Delete 수행"""
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def trash(self, request):
        """휴지통 목록 조회"""
        queryset = UserIngredient.objects.filter(user=request.user, is_deleted=True).order_by('-deleted_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """휴지통 항목 복구"""
        try:
            # 삭제된 항목도 포함해서 검색
            instance = UserIngredient.objects.get(pk=pk, user=request.user)
            instance.is_deleted = False
            instance.deleted_at = None
            instance.save()
            return Response({'status': 'restored'}, status=status.HTTP_200_OK)
        except UserIngredient.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=True, methods=['delete'])
    def hard_delete(self, request, pk=None):
        """영구 삭제"""
        try:
            instance = UserIngredient.objects.get(pk=pk, user=request.user)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserIngredient.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserIngredientListSerializer
        return UserIngredientSerializer
    
    def update(self, request, *args, **kwargs):
        """수정 요청 시 에러 상세 로깅"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            print(f"❌ [Update Error] Data: {request.data}")
            print(f"❌ [Update Error] Validation: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
    
    def get_ai_correction(self, raw_text):
        """SSAFY GMS를 사용하여 오타나 불완전한 텍스트 교정 (GPT-4o mini)"""
        gms_key = getattr(settings, 'GMS_KEY', None)
        if not gms_key:
            return None
            
        # 올바른 GPT-4o mini 엔드포인트!
        url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
        
        prompt = f"""다음은 마트 영수증에서 OCR로 읽은 글자입니다: "{raw_text}"

이 글자가 어떤 식재료/식품인지 추측해서 교정해주세요.

규칙:
1. 브랜드명(노브랜드, CJ, 농심, 오뚜기 등) 제거
2. 숫자, 가격 정보 제거  
3. 교정된 식재료명만 간단히 응답 (다른 설명 없이)

예시:
- "노브랜드 곳밀크우" → "우유"
- "농심 올리브찌파게" → "짜파게티"

입력: {raw_text}
응답:"""
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {gms_key}"  # Bearer 토큰 방식!
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 50
            }
            
            print(f"  🤖 AI 요청 중... (GPT-4o mini)")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"  📡 AI 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' not in result or len(result['choices']) == 0:
                    print(f"  ⚠️ AI 응답에 choices 없음: {result}")
                    return None
                
                choice = result['choices'][0]
                if 'message' not in choice or 'content' not in choice['message']:
                    print(f"  ⚠️ AI 응답에 message.content 없음")
                    return None
                
                corrected = choice['message']['content'].strip()
                print(f"  ✅ AI 원본 응답: '{corrected}'")
                
                corrected = re.sub(r'["`\']', '', corrected).strip()
                
                if len(corrected) > 30 or len(corrected) < 2:
                    print(f"  ⚠️ AI 응답 길이 이상: {len(corrected)}")
                    return None
                
                return corrected
            else:
                print(f"  ❌ AI 에러 응답: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"  ❌ AI 예외: {str(e)}")
            return None

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        soon_date = date.today() + timedelta(days=3)
        expiring_ingredients = self.get_queryset().filter(
            expiry_date__lte=soon_date,
            expiry_date__gte=date.today()
        )
        
        serializer = UserIngredientListSerializer(expiring_ingredients, many=True)
        return Response({
            'count': expiring_ingredients.count(),
            'ingredients': serializer.data
        })
    
    @action(
        detail=False, 
        methods=['post'], 
        permission_classes=[permissions.AllowAny],
        authentication_classes=[]
    )
    def scan(self, request):
        """영수증 스캔 - 스마트 재료명 매칭"""
        serializer = IngredientScanSerializer(data=request.data)
        
        if serializer.is_valid():
            image = serializer.validated_data['image']
            
            try:
                import easyocr
                from PIL import Image as PILImage
                import numpy as np
                from master.models import IngredientMaster
                from difflib import SequenceMatcher
                
                image.seek(0)
                img = PILImage.open(image)
                
                print(f'\n{"="*60}\n🖼️  OCR Scanning...')
                
                reader = easyocr.Reader(['ko', 'en'], gpu=False)
                img_array = np.array(img)
                results = reader.readtext(img_array)
                all_lines = [detection[1].strip() for detection in results]
                
                # 구매 날짜 추출
                purchase_date = None
                for line in all_lines[:15]:
                    match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', line)
                    if match:
                        purchase_date = match.group(1)
                        break
                
                # 번호 줄 찾기
                numbered_indices = []
                for idx, line in enumerate(all_lines):
                    if re.match(r'^\d{1,3}[\*\#]?$', line.strip()) or re.match(r'^\d{1,3}\s+[가-힣]', line):
                        numbered_indices.append(idx)
                
                all_items = []
                footer_patterns = [r'^\(*\s*면세', r'^\(*\s*과세', r'부가\s*세', r'합\s*계']
                
                # 마스터 데이터 로드 (매칭 효율을 위해)
                masters = list(IngredientMaster.objects.all())
                
                def normalize_name(name):
                    """이름 정규화: 공백 제거, 소문자화, 괄호 내용 제거"""
                    if not name: return ""
                    # 괄호와 그 안의 내용 제거 (예: "달걀(10구)" -> "달걀")
                    name = re.sub(r'\(.*\)', '', name)
                    return name.replace(" ", "").lower()

                def find_best_match(text, masters_list):
                    if not text or len(text) < 1: return None
                    
                    target = normalize_name(text)
                    
                    # 동의어 맵
                    synonyms = {
                        '계란': '달걀', '특란': '달걀', '대란': '달걀', '소란': '달걀', '왕란': '달걀', '유정란': '달걀',
                        '쇠고기': '소고기',
                        '닭': '닭고기', '돼지': '돼지고기', '오리': '오리고기',
                        '무우': '무', '공기밥': '밥',
                        '두유': '콩우유', '콩밀크': '콩우유',
                        '청양고추': '고추', '풋고추': '고추', '홍고추': '고추',
                        '대파': '파', '쪽파': '파',
                    }
                    for k, v in synonyms.items():
                        if k in target: target = target.replace(k, v)

                    # 1. Exact match (Normalized)
                    for m in masters_list:
                        if normalize_name(m.name) == target: return m
                        
                    # 2. Synonym direct match
                    if target in synonyms:
                        target = synonyms[target]
                        for m in masters_list:
                            if normalize_name(m.name) == target: return m

                    # 3. DB name is in text (e.g., "대추방울토마토" -> "토마토")
                    potential_matches = [m for m in masters_list if normalize_name(m.name) in target and len(normalize_name(m.name)) >= 2]
                    if potential_matches:
                        return max(potential_matches, key=lambda x: len(x.name))
                        
                    # 4. text is in DB name (e.g., "방울토" -> "방울토마토")
                    potential_matches = [m for m in masters_list if target in normalize_name(m.name) and len(target) >= 2]
                    if potential_matches:
                        return max(potential_matches, key=lambda x: len(x.name))
                        
                    # 5. Fuzzy match (SequenceMatcher)
                    best_score, best_match = 0, None
                    for m in masters_list:
                        score = SequenceMatcher(None, target, normalize_name(m.name)).ratio()
                        if score > best_score and score >= 0.7:
                            best_score, best_match = score, m
                    return best_match

                for i, start_idx in enumerate(numbered_indices):
                    end_idx = numbered_indices[i + 1] if i < len(numbered_indices) - 1 else len(all_lines)
                    item_lines = all_lines[start_idx:end_idx]
                    
                    if not item_lines or any(re.search(p, ' '.join(item_lines)) for p in footer_patterns):
                        continue
                    
                    first_line = item_lines[0]
                    item_number_match = re.match(r'^(\d{1,3}[\*\#]?)\s*(.*)', first_line)
                    first_line_name = item_number_match.group(2).strip() if item_number_match else ""
                    
                    name_parts = [first_line_name] if len(re.findall(r'[가-힣]', first_line_name)) >= 2 else []
                    for line in item_lines[1:]:
                        if len(re.findall(r'[가-힣]', line)) >= 2:
                            if re.search(r'\d{1,3}(,\d{3})+', line): break
                            name_parts.append(line.strip())
                        elif name_parts: break
                    
                    if not name_parts: continue
                    
                    item_name = ' '.join(name_parts)
                    item_name = re.sub(r'[\(\)\*\#\~\[\]]', ' ', item_name)
                    # 수량/규격 관련 숫자 및 단위 제거 (매칭률 향상)
                    item_name = re.sub(r'[\d.,]+\s*(L|ml|g|kg|팩|입|개|봉|속|병).*', '', item_name, flags=re.IGNORECASE)
                    item_name = re.sub(r'\s+', ' ', item_name).strip()
                    original_name = item_name
                    
                    if not item_name: continue
                    
                    print(f'  🔍 Searching for: "{item_name}"')
                    
                    
                    # 불필요한 텍스트 필터링 (대폭 확장!)
                    skip_keywords = [
                        # 금액/결제 관련
                        '금액', '합계', '결제', '카드', '현금', '포인트', '할인', '원', '총', 
                        '부가세', '면세', '과세', '대상', '적립', '잔액', '거스름돈',
                        '단가', '수량', '가액', '거스름', '공급', '세액', '매가',
                        
                        # 배송/주문 관련
                        '배송', '도착', '출발', '완료', '준비', '처리', '접수', '확인',
                        '주문', '구매', '취소', '교환', '반품',
                        
                        # 쇼핑몰/서비스 관련
                        '로켓', '프레시', '새벽배송', '샛별배송', '당일배송',
                        '상품', '내역', '관리', '바로', '선택', '목록', '품목',
                        
                        # 카테고리/라벨
                        '신선식품', '냉장', '냉동', '상온', '실온',
                        '무료배송', '쿠폰', '이벤트',
                        
                        # 기타 영수증 정보
                        '영수증', '거래명세서', '전표', '번호', '일시', '매장', '사업자',
                        '대표', '전화', '주소', '영업', '승인', '매출', '점포', '지점',
                    ]
                    
                    if any(kw in item_name for kw in skip_keywords):
                        print(f'[OCR-DEBUG] ⏭️ 스킵 (불필요 텍스트): "{item_name}"')
                        continue
                    
                    # 1~4. 개선된 매칭 시도
                    matched_master = find_best_match(item_name, masters)

                    # 5. [NEW] AI 기반 텍스트 교정 (조건 완화!)
                    if not matched_master and len(item_name) >= 3:
                        cleaned_for_ai = re.sub(r'\d+[a-zA-Z]*/?박스?|g|ml|kg|L', '', item_name).strip()
                        
                        korean_ratio = len(re.findall(r'[가-힣]', cleaned_for_ai)) / len(cleaned_for_ai) if len(cleaned_for_ai) > 0 else 0
                        digit_ratio = len(re.findall(r'\d', cleaned_for_ai)) / len(cleaned_for_ai) if len(cleaned_for_ai) > 0 else 0
                        
                        if korean_ratio >= 0.4 and digit_ratio < 0.6 and len(cleaned_for_ai) >= 2:
                            ai_suggested = self.get_ai_correction(cleaned_for_ai)
                            if ai_suggested:
                                item_name = ai_suggested
                                matched_master = find_best_match(ai_suggested, masters)
                    
                    # 6. 설정값 결정
                    final_name = item_name
                    category, storage_method, days, unit, icon = '가공식품', '냉장', 14, '개', '🍴'
                    
                    if matched_master:
                        final_name = matched_master.name
                        category = matched_master.category
                        unit = matched_master.default_unit or '개'
                        icon = matched_master.icon or '📦'
                        storage_settings = {
                            '채소': ('냉장', 7), '과일': ('냉장', 10), '육류': ('냉장', 3),
                            '수산물': ('냉장', 2), '유제품': ('냉장', 14), '음료': ('냉장', 30),
                            '면/식품/오일': ('실온', 60), '가공식품': ('냉동', 30),
                        }
                        storage_method, days = storage_settings.get(category, ('냉장', 14))
                    
                    # 수량 파싱
                    quantity = 1
                    for line in item_lines[1:]:
                        nums = re.findall(r'\b(\d{1,2})\b', line)
                        if nums:
                            quantity = int(nums[0])
                            break
                    
                    # 유통기한
                    base_date = datetime.strptime(purchase_date, '%Y-%m-%d') if purchase_date else datetime.now()
                    expiry_date = (base_date + timedelta(days=days)).strftime('%Y-%m-%d')
                    
                    # 중복 병합 로직: 이름, 카테고리, 유통기한이 같으면 수량 합산
                    is_duplicate = False
                    for existing_item in all_items:
                        if (existing_item['name'] == final_name and 
                            existing_item['category'] == category and 
                            existing_item['expiry_date'] == expiry_date):
                            existing_item['quantity'] += quantity
                            is_duplicate = True
                            print(f'[OCR-DEBUG] 🔄 중복 항목 병합: "{final_name}" 수량 {existing_item["quantity"]}로 증가')
                            break
                    
                    if not is_duplicate:
                        all_items.append({
                            'original_text': ' '.join(item_lines[:3]),
                            'name': final_name,
                            'category': category,
                            'quantity': quantity,
                            'unit': unit,
                            'icon': icon,
                            'storage_method': storage_method,
                            'expiry_date': expiry_date,
                            'purchase_date': purchase_date,
                        })
                        print(f'[OCR-DEBUG] 📝 Added to Response: "{final_name}"')
                
                # [FALLBACK] 번호 패턴이 없는 경우 - 모든 라인을 마스터와 직접 매칭 시도
                if len(all_items) == 0 and len(all_lines) > 0:
                    print(f'[OCR-DEBUG] ⚠️ 번호 패턴 없음 - Fallback 매칭 진입 ({len(all_lines)}라인)')
                    seen_names = set()
                    for line in all_lines:
                        # 기본 정제
                        clean_line = re.sub(r'[\d,\.\*\#\(\)\[\]]', '', line).strip()
                        if len(clean_line) < 2:
                            continue
                        
                        # 불필요한 텍스트 스킵 (Fallback도 동일 필터 적용!)
                        skip_keywords = [
                            '금액', '합계', '결제', '카드', '현금', '포인트', '할인', '원', '총',
                            '부가세', '면세', '과세', '대상', '적립', '잔액', '거스름돈',
                            '배송', '도착', '출발', '완료', '준비', '처리', '접수', '확인',
                            '주문', '구매', '취소', '교환', '반품',
                            '로켓', '프레시', '새벽배송', '샛별배송', '당일배송',
                            '상품', '내역', '관리', '바로', '선택', '목록',
                            '신선식품', '냉장', '냉동', '상온', '실온',
                            '무료배송', '쿠폰', '이벤트',
                            '영수증', '거래명세서', '전표', '번호', '일시', '매장',
                        ]
                        
                        if any(kw in clean_line for kw in skip_keywords):
                            continue
                        
                        original_line = clean_line
                        
                        # 1차: DB 매칭 시도
                        matched_master = find_best_match(clean_line, masters)
                        
                        # 2차: DB 매칭 실패 시 AI 교정 시도!
                        if not matched_master and len(clean_line) >= 3:
                            # 숫자/단위 제거한 버전으로 AI 호출
                            cleaned_for_ai = re.sub(r'\d+[a-zA-Z]*/?박스?|g|ml|kg|L', '', clean_line).strip()
                            
                            korean_ratio = len(re.findall(r'[가-힣]', cleaned_for_ai)) / len(cleaned_for_ai) if len(cleaned_for_ai) > 0 else 0
                            digit_ratio = len(re.findall(r'\d', cleaned_for_ai)) / len(cleaned_for_ai) if len(cleaned_for_ai) > 0 else 0
                            
                            if korean_ratio >= 0.4 and digit_ratio < 0.6 and len(cleaned_for_ai) >= 2:
                                print(f'[FALLBACK] 🔍 AI 보정 시도: "{cleaned_for_ai}"')
                                ai_suggested = self.get_ai_correction(cleaned_for_ai)
                                if ai_suggested:
                                    print(f'[FALLBACK] 🤖 AI 제안: "{ai_suggested}"')
                                    clean_line = ai_suggested
                                    matched_master = find_best_match(ai_suggested, masters)
                                    if matched_master:
                                        print(f'[FALLBACK] ✅ AI 보정 & DB 매칭 성공: "{original_line}" -> "{matched_master.name}"')
                        
                        if matched_master and matched_master.name not in seen_names:
                            seen_names.add(matched_master.name)
                            category = matched_master.category
                            unit = matched_master.default_unit or '개'
                            icon = matched_master.icon or '📦'
                            storage_settings = {
                                '채소': ('냉장', 7), '과일': ('냉장', 10), '육류': ('냉장', 3),
                                '수산물': ('냉장', 2), '유제품': ('냉장', 14), '음료': ('냉장', 30),
                                '면/식품/오일': ('실온', 60), '가공식품': ('냉동', 30),
                            }
                            storage_method, days = storage_settings.get(category, ('냉장', 14))
                            base_date = datetime.strptime(purchase_date, '%Y-%m-%d') if purchase_date else datetime.now()
                            expiry_date = (base_date + timedelta(days=days)).strftime('%Y-%m-%d')
                            
                            all_items.append({
                                'original_text': line,
                                'name': matched_master.name,
                                'category': category,
                                'quantity': 1,
                                'unit': unit,
                                'icon': icon,
                                'storage_method': storage_method,
                                'expiry_date': expiry_date,
                                'purchase_date': purchase_date,
                            })
                            print(f'[FALLBACK] 📝 Added: "{matched_master.name}" from "{line}"')
                
                return Response({
                    'message': f'인식 완료 ({len(all_items)}개)',
                    'items': all_items,
                    'purchase_date': purchase_date
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, 
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def identify_ingredients_ai(self, request):
        """Gemini 2.0 Flash를 사용하여 사진 제로 식재료 및 수량 분석"""
        serializer = IngredientScanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        gms_key = getattr(settings, 'GMS_KEY', None)
        if not gms_key:
            return Response({'error': 'GMS API Key가 설정되지 않았습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        image = serializer.validated_data['image']
        import base64
        import json
        from master.models import IngredientMaster
        from PIL import Image as PILImage
        from io import BytesIO
        
        try:
            # 이미지 리사이즈 (GMS API 크기 제한 대응)
            image.seek(0)
            pil_image = PILImage.open(image)
            
            original_width, original_height = pil_image.width, pil_image.height
            print(f"\n[VISION-DEBUG] 📸 이미지 분석 시작 (Gemini 2.5 Flash)")
            print(f"[VISION-DEBUG]  - 원본 크기: {original_width}x{original_height}")
            
            # RGB 변환 (RGBA나 다른 모드 처리)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 최대 크기 제한 (800px)
            max_size = 800
            if pil_image.width > max_size or pil_image.height > max_size:
                pil_image.thumbnail((max_size, max_size), PILImage.Resampling.LANCZOS)
                print(f"[VISION-DEBUG]  - 압축 후 크기: {pil_image.width}x{pil_image.height} (품질 75%)")
            else:
                print(f"[VISION-DEBUG]  - 압축 불필요 (이미 {max_size}px 이하)")
            
            # 압축된 JPEG로 변환 (품질 75%)
            buffer = BytesIO()
            pil_image.save(buffer, format='JPEG', quality=75, optimize=True)
            buffer.seek(0)
            
            # base64 인코딩
            image_data = base64.b64encode(buffer.read()).decode('utf-8')
            
            url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gms_key}"
            
            prompt = """
            이 사진 속에서 식별되는 모든 식재료를 찾아서 JSON 배열 형식으로만 응답해주세요.
            다른 설명은 절대 하지 마세요.
            JSON 필드:
            - name: 식재료명 (예: 사과, 우유, 고기)
            - quantity: 식별되는 대략적인 수량 (숫자만, 모르면 1)
            - unit: 단위 (개, 봉, 팩 등 가장 적절한 것)
            
            형식 예시:
            [{"name": "사과", "quantity": 3, "unit": "개"}, {"name": "우유", "quantity": 1, "unit": "개"}]
            """
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            print(f"\n[VISION-DEBUG] 📸 이미지 분석 시작")
            print(f"[VISION-DEBUG]  - 이미지 크기: {pil_image.width}x{pil_image.height}")
            print(f"[VISION-DEBUG] 🤖 Gemini Vision API 호출 중...")
            
            import requests
            response = requests.post(url, json=payload, timeout=30)
            print(f"[VISION-DEBUG] 📡 응답 상태: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[VISION-DEBUG] ❌ API 에러: {response.text[:500]}")
                return Response({'error': f'AI 연동 실패: {response.text}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            result = response.json()
            raw_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
            print(f"[VISION-DEBUG] ✅ AI 응답 받음 (길이: {len(raw_text)} chars)")
            
            # Markdown code block 제거
            clean_json = re.sub(r'```json\s*|\s*```', '', raw_text)
            items_data = json.loads(clean_json)
            print(f"[VISION-DEBUG] 📦 인식된 아이템 수: {len(items_data)}")
            
            # 마스터 데이터와 매칭하여 상세 정보 보강
            masters = list(IngredientMaster.objects.all())
            final_items = []
            
            def normalize_name(name):
                if not name: return ""
                name = re.sub(r'\(.*\)', '', name)
                return name.replace(" ", "").lower()

            def find_best_match(text, masters_list):
                if not text: return None
                target = normalize_name(text)
                
                synonyms = {'계란': '달걀', '쇠고기': '소고기', '닭': '닭고기', '돼지': '돼지고기'}
                for k, v in synonyms.items():
                    if k in target: target = target.replace(k, v)

                for m in masters_list:
                    if normalize_name(m.name) == target: return m
                for m in masters_list:
                    m_norm = normalize_name(m.name)
                    if m_norm in target or target in m_norm: return m
                return None

            for item in items_data:
                name = item.get('name')
                matched_master = find_best_match(name, masters)
                
                category, storage_method, days, unit, icon = '가공식품', '냉장', 14, item.get('unit', '개'), '🍴'
                
                if matched_master:
                    name = matched_master.name
                    category = matched_master.category
                    unit = matched_master.default_unit or unit
                    icon = matched_master.icon or '📦'
                    storage_settings = {
                        '채소': ('냉장', 7), '과일': ('냉장', 10), '육류': ('냉장', 3),
                        '수산물': ('냉장', 2), '유제품': ('냉장', 14), '음료': ('냉장', 30),
                        '면/식품/오일': ('실온', 60), '가공식품': ('냉동', 30),
                    }
                    storage_method, days = storage_settings.get(category, ('냉장', 14))
                
                expiry_date = (date.today() + timedelta(days=days)).strftime('%Y-%m-%d')
                
                final_items.append({
                    'name': name,
                    'category': category,
                    'quantity': item.get('quantity', 1),
                    'unit': unit,
                    'icon': icon,
                    'storage_method': storage_method,
                    'expiry_date': expiry_date,
                    'is_ai_identified': True
                })
                
            return Response({
                'message': f'AI 분석 완료 ({len(final_items)}개 식별)',
                'items': final_items
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f'분석 중 오류 발생: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        ingredients_data = request.data.get('ingredients', [])
        if not ingredients_data:
            return Response({'error': '데이터가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        from master.models import IngredientMaster
        created_ingredients = []
        failed_items = []
        
        for data in ingredients_data:
            try:
                # 신규 마스터 등록
                name = data.get('name')
                if name and not IngredientMaster.objects.filter(name=name).exists():
                    IngredientMaster.objects.create(
                        name=name, category=data.get('category', '가공식품'),
                        default_unit=data.get('unit', '개'), icon=data.get('icon', '🍴'),
                        api_source='UserScan'
                    )
                
                # 보관함용 데이터 정제
                # 제외할 키 목록 (frontend state 관리용 키들)
                exclude_keys = ['id', 'original_text', 'original_name', 'selected', 'matched', 
                                'icon', 'purchase_date', 'showAutocomplete', 'autocompleteResults', 'isComposing']
                clean_data = {k: v for k, v in data.items() if k not in exclude_keys}
                
                # 빈 값 처리 (수량이 없으면 1)
                if 'quantity' not in clean_data or clean_data['quantity'] == '':
                    clean_data['quantity'] = 1
                
                serializer = UserIngredientSerializer(data=clean_data, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    created_ingredients.append(serializer.data)
                else:
                    print(f"❌ [Batch Create Error] Item: {name}")
                    print(f"❌ [Batch Create Error] Validation: {serializer.errors}")
                    failed_items.append({
                        'name': name,
                        'errors': serializer.errors
                    })
            except Exception as e:
                print(f"❌ [Batch Create Exception] Item: {data.get('name')} - {str(e)}")
                failed_items.append({
                    'name': data.get('name', 'Unknown'),
                    'errors': str(e)
                })
        
        response_data = {
            'message': f'{len(created_ingredients)}개 저장 완료, {len(failed_items)}개 실패',
            'created': created_ingredients,
            'failed': failed_items
        }
        
        status_code = status.HTTP_201_CREATED
        if len(failed_items) > 0 and len(created_ingredients) == 0:
            status_code = status.HTTP_400_BAD_REQUEST
        elif len(failed_items) > 0:
            status_code = status.HTTP_206_PARTIAL_CONTENT  # or 207 Multi-Status if supported, but 206/201 is safer for basic clients
            
        return Response(response_data, status=status_code)

    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """재료 소진 - 수량 차감"""
        ingredient = self.get_object()
        quantity = float(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response({'error': '차감할 수량이 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity >= ingredient.quantity:
            # 전체 소진 (소진은 휴지통 안감? or 소진 기록? 일단 사용자 요구는 '버리기'만 휴지통)
            # 소비는 실제로 먹어서 없어진 거라 삭제가 맞음 (또는 소비 로그 기록)
            ingredient.delete() 
            return Response({
                'message': '재료가 모두 소진되었습니다.',
                'remaining_quantity': 0,
                'deleted': True
            })
        
        # 부분 차감
        ingredient.quantity -= quantity
        ingredient.save()
        
        return Response({
            'message': f'{quantity}{ingredient.unit} 차감되었습니다.',
            'remaining_quantity': ingredient.quantity,
            'deleted': False
        })

    @action(detail=True, methods=['post'])
    def discard(self, request, pk=None):
        """재료 부분 버리기 - 수량 차감 및 차감분을 휴지통으로 생성"""
        ingredient = self.get_object()
        quantity = float(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response({'error': '버릴 수량이 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 전체 버리기와 같거나 많으면 -> 해당 재료 Soft Delete
        if quantity >= ingredient.quantity:
            ingredient.is_deleted = True
            ingredient.deleted_at = timezone.now()
            ingredient.save()
            return Response({
                'message': '재료를 모두 휴지통에 버렸습니다.',
                'remaining_quantity': 0,
                'discarded': True
            })
        
        # 부분 버리기
        ingredient.quantity -= quantity
        ingredient.save()
        
        # 버려진 수량만큼의 '삭제된' 새 아이템 생성 (휴지통용)
        UserIngredient.objects.create(
            user=self.request.user,
            ingredient_master=ingredient.ingredient_master,
            name=ingredient.name,
            category=ingredient.category,
            quantity=quantity,
            unit=ingredient.unit,
            storage_method=ingredient.storage_method,
            expiry_date=ingredient.expiry_date,
            purchase_date=ingredient.purchase_date,
            icon=ingredient.icon,
            is_deleted=True,
            deleted_at=timezone.now()
        )
        
        return Response({
            'message': f'{quantity}{ingredient.unit} 휴지통에 버렸습니다.',
            'remaining_quantity': ingredient.quantity,
            'discarded': False
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """선택한 여러 식재료를 한 번에 휴지통으로"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '삭제할 항목이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Soft Delete
        self.get_queryset().filter(id__in=ids).update(is_deleted=True, deleted_at=timezone.now())
        return Response({'message': '선택한 항목들이 휴지통으로 이동되었습니다.'})

    @action(detail=False, methods=['post'])
    def clear_expired(self, request):
        """유통기한이 지난 모든 식재료를 휴지통으로"""
        expired_items = self.get_queryset().filter(expiry_date__lt=date.today())
        count = expired_items.count()
        if count == 0:
            return Response({'message': '정리할 재료가 없습니다.'})
            
        expired_items.update(is_deleted=True, deleted_at=timezone.now())
        return Response({'message': f'유통기한이 지난 {count}개의 항목을 모두 휴지통으로 보냈습니다.'})
