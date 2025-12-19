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
                    
                    # 상품명 찾기 (한글이 2글자 이상 있는 첫 번째 줄)
                    item_name = None
                    for line in item_lines[1:]:  # 번호 다음부터
                        if len(re.findall(r'[가-힣]', line)) >= 2:
                            item_name = line
                            break
                    
                    if not item_name:
                        print(f'  ❌ No valid name found')
                        continue
                    
                    # 상품명 정리
                    item_name = re.sub(r'[\(\)\*\#\~\[\]]', ' ', item_name)
                    item_name = re.sub(r'\s+', ' ', item_name).strip()
                    
                    # 수량 찾기 (쉼표 없는 1~99 사이 숫자)
                    quantity = 1
                    for line in item_lines:
                        numbers = re.findall(r'\b(\d{1,2})\b', line)  # 1~2자리 숫자
                        for num in numbers:
                            num_int = int(num)
                            if 1 <= num_int <= 99:
                                quantity = num_int
                                break
                        if quantity > 1:
                            break
                    
                    # 유통기한
                    if purchase_date:
                        try:
                            purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d')
                            expiry_dt = purchase_dt + timedelta(days=7)
                            expiry_date = expiry_dt.strftime('%Y-%m-%d')
                        except:
                            expiry_date = (date.today() + timedelta(days=7)).isoformat()
                    else:
                        expiry_date = (date.today() + timedelta(days=7)).isoformat()
                    
                    all_items.append({
                        'original_text': ' '.join(item_lines[:3]),  # 처음 3줄 표시
                        'name': item_name,
                        'quantity': quantity,
                        'unit': '개',
                        'storage_method': '냉장',
                        'expiry_date': expiry_date,
                        'purchase_date': purchase_date
                    })
                    
                    print(f'  ✅ {item_name} x {quantity}')
                
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
        
        if not ingredients_data:
            return Response({
                'error': '추가할 식재료가 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_ingredients = []
        errors = []
        
        for idx, ingredient_data in enumerate(ingredients_data):
            try:
                ingredient_data.pop('purchase_date', None)
                ingredient_data['user'] = request.user.id
                
                serializer = UserIngredientSerializer(data=ingredient_data)
                if serializer.is_valid():
                    ingredient = serializer.save(user=request.user)
                    created_ingredients.append(serializer.data)
                else:
                    errors.append({
                        'index': idx,
                        'data': ingredient_data,
                        'errors': serializer.errors
                    })
            except Exception as e:
                errors.append({
                    'index': idx,
                    'data': ingredient_data,
                    'errors': str(e)
                })
        
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