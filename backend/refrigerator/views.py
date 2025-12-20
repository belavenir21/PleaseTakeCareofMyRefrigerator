from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as filters
from datetime import date, timedelta, datetime
from django.conf import settings
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
        return UserIngredient.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserIngredientListSerializer
        return UserIngredientSerializer
    
    def get_ai_correction(self, raw_text):
        """SSAFY GMS를 사용하여 오타나 불완전한 텍스트 교정"""
        gms_key = getattr(settings, 'GMS_KEY', None)
        if not gms_key:
            return None
            
        url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gms_key}"
        
        prompt = f"""
        다음은 영수즘 OCR 인식 결과 중 일부입니다. 
        불완전하게 인식되었거나 오타가 있다면 한국에서 판매되는 가장 가능성 높은 식품/식재료명 1개로만 교정해주세요.
        다른 설명 없이 교정한 단어 그 자체만 응답하세요.
        입력: {raw_text}
        응답:
        """
        
        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json()
                corrected = result['candidates'][0]['content']['parts'][0]['text'].strip()
                corrected = re.sub(r'["\']', '', corrected).strip()
                return corrected
        except Exception as e:
            print(f"  ❌ AI Correction Error: {str(e)}")
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
                
                def find_best_match(text, masters_list):
                    if not text or len(text) < 2: return None
                    
                    # 1. Exact match
                    for m in masters_list:
                        if m.name == text: return m
                        
                    # 2. DB name is in text (e.g., "대추방울토마토" -> "토마토")
                    potential_matches = [m for m in masters_list if m.name in text and len(m.name) >= 2]
                    if potential_matches:
                        return max(potential_matches, key=lambda x: len(x.name))
                        
                    # 3. text is in DB name (e.g., "방울토" -> "방울토마토")
                    potential_matches = [m for m in masters_list if text in m.name and len(text) >= 2]
                    if potential_matches:
                        return max(potential_matches, key=lambda x: len(x.name))
                        
                    # 4. Fuzzy match (SequenceMatcher)
                    best_score, best_match = 0, None
                    for m in masters_list:
                        score = SequenceMatcher(None, text, m.name).ratio()
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
                    
                    # 1~4. 개선된 매칭 시도
                    matched_master = find_best_match(item_name, masters)

                    # 5. [NEW] AI 기반 텍스트 교정
                    if not matched_master:
                        print(f'\n[OCR-DEBUG] 🔍 AI 보정 시도: "{item_name}"')
                        ai_suggested = self.get_ai_correction(item_name)
                        if ai_suggested:
                            print(f'[OCR-DEBUG] 🤖 AI 제안: "{ai_suggested}"')
                            
                            # AI 제안이 있으면 일단 반영
                            item_name = ai_suggested
                            
                            # AI 제안값으로 다시 한 번 정밀 매칭
                            matched_master = find_best_match(ai_suggested, masters)
                            
                            if matched_master:
                                print(f'[OCR-DEBUG] ✅ AI 보정 & DB 매칭 성공: "{original_name}" -> "{matched_master.name}"')
                            else:
                                print(f'[OCR-DEBUG] ⚠️ AI 보정 적용 (DB 미존재): "{original_name}" -> "{item_name}"')
                        else:
                            print(f'[OCR-DEBUG] ❓ AI 보정 제안 없음')

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
                    
                    print(f'[OCR-DEBUG] 🏁 최종 결정 항목: "{final_name}" ({category})\n')

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
                
                return Response({
                    'message': f'인식 완료 ({len(all_items)}개)',
                    'items': all_items,
                    'purchase_date': purchase_date
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        ingredients_data = request.data.get('ingredients', [])
        if not ingredients_data:
            return Response({'error': '데이터가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        from master.models import IngredientMaster
        created_ingredients = []
        
        for data in ingredients_data:
            # 신규 마스터 등록
            name = data.get('name')
            if not IngredientMaster.objects.filter(name=name).exists():
                IngredientMaster.objects.create(
                    name=name, category=data.get('category', '가공식품'),
                    default_unit=data.get('unit', '개'), icon=data.get('icon', '🍴'),
                    api_source='UserScan'
                )
            
            # 보관함용 데이터 정제
            clean_data = {k: v for k, v in data.items() if k not in ['id', 'original_text', 'original_name', 'selected', 'matched', 'icon', 'purchase_date']}
            
            serializer = UserIngredientSerializer(data=clean_data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                created_ingredients.append(serializer.data)
        
        return Response({'message': f'{len(created_ingredients)}개 저장 완료'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        ingredient = self.get_object()
        quantity = request.data.get('quantity', 0)
        if quantity >= ingredient.quantity:
            ingredient.delete()
            return Response({'message': '소진 완료'})
        ingredient.quantity -= quantity
        ingredient.save()
        return Response({'remaining': ingredient.quantity})

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """선택한 여러 식재료를 한 번에 삭제"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '삭제할 항목이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'message': f'{deleted_count}개의 항목이 삭제되었습니다.'})

    @action(detail=False, methods=['post'])
    def clear_expired(self, request):
        """유통기한이 지난 모든 식재료를 삭제"""
        expired_items = self.get_queryset().filter(expiry_date__lt=date.today())
        count = expired_items.count()
        if count == 0:
            return Response({'message': '정리할 재료가 없습니다.'})
            
        expired_items.delete()
        return Response({'message': f'유통기한이 지난 {count}개의 항목을 모두 정리했습니다.'})