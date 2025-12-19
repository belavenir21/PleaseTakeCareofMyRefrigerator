from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as filters
from datetime import date, timedelta, datetime
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
        """영수증 스캔 - 쪼개진 줄 합치기"""
        serializer = IngredientScanSerializer(data=request.data)
        
        if serializer.is_valid():
            image = serializer.validated_data['image']
            
            try:
                import easyocr
                from PIL import Image as PILImage
                import re
                import numpy as np
                
                image.seek(0)
                img = PILImage.open(image)
                
                print(f'\n{"="*60}')
                print(f'🖼️  Image size: {img.size}')
                print(f'{"="*60}')
                
                reader = easyocr.Reader(['ko', 'en'], gpu=False)
                img_array = np.array(img)
                results = reader.readtext(img_array)
                
                print(f'✅ OCR completed - {len(results)} text blocks\n')
                
                all_lines = [detection[1].strip() for detection in results]
                
                # 구매 날짜 추출
                purchase_date = None
                for line in all_lines[:15]:
                    match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', line)
                    if match:
                        purchase_date = match.group(1)
                        print(f'📅 Purchase date: {purchase_date}\n')
                        break
                
                # ===== 핵심: 번호 줄부터 다음 번호 줄까지 합치기 =====
                numbered_indices = []
                for idx, line in enumerate(all_lines):
                    # 01*, 02, 03 같은 번호 패턴
                    if re.match(r'^\d{1,2}[\*\#]?$', line.strip()):
                        numbered_indices.append(idx)
                
                print(f'🔢 Found {len(numbered_indices)} item numbers: {numbered_indices}\n')
                
                all_items = []
                
                # Footer 키워드 (더 구체적으로)
                footer_patterns = [
                    r'^\(*\s*면세',
                    r'^\(*\s*과세', 
                    r'부가\s*세',
                    r'합\s*계',
                ]
                
                print('🔍 Parsing items:')
                print('-' * 60)
                
                for i, start_idx in enumerate(numbered_indices):
                    # 다음 번호까지가 한 상품
                    if i < len(numbered_indices) - 1:
                        end_idx = numbered_indices[i + 1]
                    else:
                        end_idx = len(all_lines)
                    
                    # 번호부터 다음 번호 전까지 합치기
                    item_lines = all_lines[start_idx:end_idx]
                    
                    # 너무 짧으면 스킵 (번호 하나만 있고 내용 없음)
                    if len(item_lines) < 2:
                        continue
                    
                    item_number = item_lines[0]  # "01*"
                    
                    # Footer 도달 체크
                    if any(re.search(pattern, ' '.join(item_lines)) for pattern in footer_patterns):
                        print(f'🛑 Footer section detected at item {item_number}')
                        break
                    
                    print(f'\n  [{item_number}] Raw lines: {item_lines[:5]}')  # 처음 5줄만
                    
                    # 상품명 찾기 (한글이 포함된 여러 줄을 모두 합침)
                    name_parts = []
                    for line in item_lines[1:]:  # 번호 다음부터
                        # 한글이 2글자 이상 있으면 상품명의 일부로 취급
                        if len(re.findall(r'[가-힣]', line)) >= 2:
                            name_parts.append(line.strip())
                        # 가격이나 수량 패턴이 나오면 중단
                        elif re.search(r'\d{1,3}(,\d{3})+', line) or len(name_parts) > 0:
                            break
                    
                    if not name_parts:
                        print(f'  ❌ No valid name found')
                        continue
                    
                    # 여러 줄을 공백으로 연결
                    item_name = ' '.join(name_parts)
                    
                    # 상품명 정리
                    item_name = re.sub(r'[\(\)\*\#\~\[\]]', ' ', item_name)
                    item_name = re.sub(r'\s+', ' ', item_name).strip()
                    
                    # ===== 스마트 재료명 매칭 =====
                    from master.models import IngredientMaster
                    from difflib import SequenceMatcher
                    
                    matched_master = None
                    original_name = item_name  # OCR 원본 이름 저장
                    
                    print(f'  🔍 Searching for: "{item_name}"')
                    
                    # 1. 정확히 일치하는 재료 찾기
                    matched_master = IngredientMaster.objects.filter(name__iexact=item_name).first()
                    if matched_master:
                        print(f'  ✅ Exact match: "{item_name}" -> "{matched_master.name}"')
                    
                    if not matched_master:
                        # 2. 부분 일치하는 재료 찾기
                        # 성능을 위해 이름에 한글이 2글자 이상 포함된 경우만 검색
                        hangul_chars = re.findall(r'[가-힣]+', item_name)
                        if hangul_chars:
                            main_keyword = max(hangul_chars, key=len)  # 가장 긴 한글 부분
                            if len(main_keyword) >= 2:
                                # DB에서 해당 키워드를 포함하는 재료 찾기
                                candidates = IngredientMaster.objects.filter(name__icontains=main_keyword)[:10]
                                for master in candidates:
                                    if item_name in master.name or master.name in item_name:
                                        matched_master = master
                                        print(f'  📌 Partial match: "{item_name}" -> "{master.name}"')
                                        break
                    
                    if not matched_master:
                        # 3. 유사도 검사 (0.75 이상이면 같은 재료로 간주)
                        best_score = 0
                        best_match = None
                        # 성능을 위해 상위 100개 재료만 검사
                        for master in IngredientMaster.objects.all()[:100]:
                            score = SequenceMatcher(None, item_name, master.name).ratio()
                            if score > best_score and score >= 0.75:
                                best_score = score
                                best_match = master
                        
                        if best_match:
                            matched_master = best_match
                            print(f'  📌 Fuzzy match ({best_score:.2f}): "{item_name}" -> "{best_match.name}"')
                    
                    # 매칭된 재료가 있으면 그 이름 사용, 없으면 새로 추가
                    if matched_master:
                        item_name = matched_master.name
                        category = matched_master.category
                        default_unit = matched_master.default_unit or '개'
                        
                        # 카테고리별 기본 보관방법 및 유통기한 설정
                        storage_settings = {
                            '채소': ('냉장', 7),
                            '과일': ('냉장', 10),
                            '육류': ('냉장', 3),
                            '수산물': ('냉장', 2),
                            '유제품': ('냉장', 14),
                            '냉동식품': ('냉동', 30),
                            '곡류': ('실온', 60),
                            '가공식품': ('실온', 30),
                        }
                        storage_method, days = storage_settings.get(category, ('냉장', 14))
                        print(f'  ✅ Matched! Category: {category}, Storage: {storage_method}, Days: {days}')
                    else:
                        # DB에 없는 새로운 재료 -> IngredientMaster에 추가
                        print(f'  🆕 New ingredient: "{item_name}" - Adding to IngredientMaster')
                        new_master = IngredientMaster.objects.create(
                            name=item_name,
                            category='가공식품',  # 기본 카테고리
                            default_unit='개',
                            icon='🍴'
                        )
                        matched_master = new_master
                        storage_method = '냉장'
                        days = 14
                        default_unit = '개'
                    
                    # 수량 찾기 (영수증 형식: 번호 - 상품명 - 가격 - 개수 - 총가격)
                    quantity = 1
                    # 첫 번째 줄(항목 번호)을 제외하고 탐색
                    for idx, line in enumerate(item_lines[1:], 1):  # 번호 다음부터
                        # 가격 패턴(1,000 이상 또는 쉼표 포함)이 아닌 1~99 사이 숫자 찾기
                        if not re.search(r'[,.]', line):  # 쉼표나 점이 없는 줄
                            numbers = re.findall(r'\b(\d{1,2})\b', line)  # 1~2자리 숫자
                            for num in numbers:
                                num_int = int(num)
                                # 항목 번호와 중복되지 않도록 체크
                                if 1 <= num_int <= 99 and num != item_lines[0].strip('*#'):
                                    quantity = num_int
                                    print(f'  📦 Found quantity: {quantity} in line "{line}"')
                                    break
                        if quantity > 1:
                            break
                    
                    # 유통기한 계산
                    if purchase_date:
                        try:
                            purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d')
                            expiry_dt = purchase_dt + timedelta(days=days)
                            expiry_date = expiry_dt.strftime('%Y-%m-%d')
                        except:
                            expiry_date = (date.today() + timedelta(days=days)).isoformat()
                    else:
                        expiry_date = (date.today() + timedelta(days=days)).isoformat()
                    
                    all_items.append({
                        'original_text': ' '.join(item_lines[:3]),  # OCR 원본
                        'original_name': original_name,  # OCR이 인식한 원본 이름
                        'name': item_name,  # 정규화된 이름
                        'quantity': quantity,
                        'unit': default_unit if matched_master else '개',
                        'storage_method': storage_method,
                        'expiry_date': expiry_date,
                        'purchase_date': purchase_date,
                        'matched': matched_master is not None
                    })
                    
                    match_indicator = '✅' if matched_master else '🆕'
                    print(f'  {match_indicator} {item_name} x {quantity} ({storage_method}, {days}일)')
                
                print('-' * 60)
                print(f'\n🛒 Total items: {len(all_items)}\n')
                print('=' * 60)
                
                if not all_items:
                    return Response({
                        'message': '영수증에서 상품을 찾을 수 없습니다.',
                        'items': [],
                        'purchase_date': purchase_date
                    }, status=status.HTTP_200_OK)
                
                return Response({
                    'message': f'영수증에서 {len(all_items)}개 상품을 인식했습니다.',
                    'items': all_items,
                    'purchase_date': purchase_date
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                print(f'\n❌ ERROR: {type(e).__name__}')
                print(f'   {str(e)}')
                import traceback
                traceback.print_exc()
                return Response({
                    'error': f'OCR 처리 중 오류: {str(e)}',
                    'items': []
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """여러 식재료를 한 번에 추가"""
        ingredients_data = request.data.get('ingredients', [])
        
        print(f'\n{"="*60}')
        print(f'📦 Batch Create Request')
        print(f'   User: {request.user}')
        print(f'   Items count: {len(ingredients_data)}')
        print(f'{"="*60}\n')
        
        if not ingredients_data:
            return Response({
                'error': '추가할 식재료가 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_ingredients = []
        errors = []
        
        for idx, ingredient_data in enumerate(ingredients_data):
            try:
                print(f'\n[{idx + 1}/{len(ingredients_data)}] Processing: {ingredient_data.get("name", "Unknown")}')
                print(f'   Original data: {ingredient_data}')
                
                # purchase_date 제거 (UserIngredient 모델에 없는 필드)
                if 'purchase_date' in ingredient_data:
                    ingredient_data.pop('purchase_date')
                
                # id, original_text, selected 같은 프론트엔드 전용 필드도 제거
                ingredient_data.pop('id', None)
                ingredient_data.pop('original_text', None)
                ingredient_data.pop('selected', None)
                
                # user 필드는 serializer의 create 메서드에서 처리됨
                ingredient_data.pop('user', None)
                
                print(f'   Cleaned data: {ingredient_data}')
                
                serializer = UserIngredientSerializer(
                    data=ingredient_data,
                    context={'request': request}
                )
                if serializer.is_valid():
                    ingredient = serializer.save()
                    created_ingredients.append(serializer.data)
                    print(f'   ✅ Saved successfully (ID: {ingredient.id})')
                else:
                    print(f'   ❌ Validation failed: {serializer.errors}')
                    errors.append({
                        'index': idx,
                        'name': ingredient_data.get('name', 'Unknown'),
                        'data': ingredient_data,
                        'errors': serializer.errors
                    })
            except Exception as e:
                print(f'   ❌ Exception: {type(e).__name__} - {str(e)}')
                import traceback
                traceback.print_exc()
                errors.append({
                    'index': idx,
                    'name': ingredient_data.get('name', 'Unknown'),
                    'data': ingredient_data,
                    'errors': str(e)
                })
        
        print(f'\n{"="*60}')
        print(f'✅ Success: {len(created_ingredients)} / ❌ Failed: {len(errors)}')
        print(f'{"="*60}\n')
        
        response_data = {
            'message': f'{len(created_ingredients)}개 식재료가 추가되었습니다.',
            'created': created_ingredients,
            'success_count': len(created_ingredients),
            'total_count': len(ingredients_data)
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['error_count'] = len(errors)
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """식재료 소진"""
        ingredient = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        if quantity <= 0:
            return Response({
                'error': '소진할 수량을 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity >= ingredient.quantity:
            ingredient.delete()
            return Response({
                'message': '식재료가 모두 소진되었습니다.'
            })
        else:
            ingredient.quantity -= quantity
            ingredient.save()
            
            return Response({
                'message': f'{quantity}{ingredient.unit} 소진되었습니다.',
                'remaining_quantity': ingredient.quantity
            })