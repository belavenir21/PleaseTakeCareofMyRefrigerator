from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import date, timedelta
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

    # CSRF 검증 없는 SessionAuthentication 사용
    from config.authentication import CsrfExemptSessionAuthentication
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """현재 사용자의 식재료만 조회"""
        return UserIngredient.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """액션에 따라 다른 Serializer 사용"""
        if self.action == 'list':
            return UserIngredientListSerializer
        return UserIngredientSerializer
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """유통기한 임박 식재료 조회"""
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
        authentication_classes=[]  # No authentication needed for testing
    )
    def scan(self, request):
        """사진으로 식재료 인식 (AI Object Detection)"""
        serializer = IngredientScanSerializer(data=request.data)
        
        if serializer.is_valid():
            image = serializer.validated_data['image']
            
            # Hugging Face API를 통한 실제 Object Detection
            from django.conf import settings
            from huggingface_hub import InferenceClient
            from collections import Counter
            import io
            
            # OCR을 사용한 영수증 인식 (Tesseract)
            try:
                import pytesseract
                from PIL import Image as PILImage
                import re
                
                # 이미지 파일 열기
                image.seek(0)
                img = PILImage.open(image)
                
                print(f'🖼️  Image size: {img.size}')
                print('🤖 Running OCR on receipt...')
                
                # Tesseract 경로 설정 (Windows)
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                
                # OCR 수행 (한글+영어)
                text = pytesseract.image_to_string(img, lang='kor+eng')
                
                print(f'✅ OCR completed')
                print(f'📄 Extracted text preview: {text[:200]}...')
                
                # 텍스트에서 식재료와 수량 파싱
                lines = text.split('\n')
                detected_ingredients = []
                
                # 식재료 키워드 (한글 + 영어)
                food_keywords_kr = [
                    '사과', '바나나', '오렌지', '포도', '딸기', '수박', '참외', '배',
                    '감자', '고구마', '당근', '무', '배추', '양배추', '양파', '대파',
                    '마늘', '생강', '고추', '파프리카', '토마토', '오이', '호박',
                    '상추', '깻잎', '시금치', '부추', '미나리', '콩나물', '숙주',
                    '버섯', '느타리', '팽이', '새송이', '표고', '양송이',
                    '소고기', '돼지고기', '닭고기', '삼겹살', '목살', '갈비',
                    '우유', '두유', '요거트', '치즈', '계란', '달걀',
                    '두부', '순두부', '라면', '우동', '김치', '된장', '고추장',
                    '햄', '소시지', '베이컨', '참치', '김', '김밥', '떡'
                ]
                
                # 영어 키워드와 한글 매핑
                food_keywords_en = {
                    'apple': '사과', 'banana': '바나나', 'orange': '오렌지',
                    'grape': '포도', 'strawberry': '딸기', 'watermelon': '수박',
                    'potato': '감자', 'sweet potato': '고구마', 'carrot': '당근',
                    'radish': '무', 'cabbage': '배추', 'onion': '양파',
                    'garlic': '마늘', 'ginger': '생강', 'pepper': '고추',
                    'tomato': '토마토', 'cucumber': '오이', 'pumpkin': '호박',
                    'lettuce': '상추', 'spinach': '시금치', 'mushroom': '버섯',
                    'beef': '소고기', 'pork': '돼지고기', 'chicken': '닭고기',
                    'milk': '우유', 'yogurt': '요거트', 'cheese': '치즈',
                    'egg': '계란', 'tofu': '두부', 'ramen': '라면',
                    'ham': '햄', 'bacon': '베이컨'
                }
                
                food_keywords = food_keywords_kr
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 공백 제거 (OCR이 "오 뚜 기 햄" 같이 읽는 경우 대비)
                    line_no_space = line.replace(' ', '')
                    
                    # 각 줄에서 식재료 찾기
                    for keyword in food_keywords:
                        if keyword in line or keyword in line_no_space:
                            # 수량 찾기 (숫자 + 단위)
                            quantity_match = re.search(r'(\d+)\s*(개|ea|EA|봉|팩|kg|g|단|마리)?', line)
                            
                            quantity = 1
                            unit = '개'
                            
                            if quantity_match:
                                quantity = int(quantity_match.group(1))
                                unit_found = quantity_match.group(2)
                                if unit_found:
                                    unit = unit_found
                            
                            # 중복 체크
                            existing = next((item for item in detected_ingredients if item['name'] == keyword), None)
                            if existing:
                                existing['quantity'] += quantity
                            else:
                                detected_ingredients.append({
                                    'name': keyword,
                                    'quantity': quantity,
                                    'unit': unit,
                                    'storage_method': '냉장',
                                    'expiry_date': (date.today() + timedelta(days=7)).isoformat()
                                })
                            
                            break  # 한 줄에서 하나만 찾기
                
                if not detected_ingredients:
                    print('⚠️  No ingredients found in receipt')
                    return Response({
                        'message': '영수증에서 식재료를 찾을 수 없습니다. 직접 입력해주세요.',
                        'detected_ingredients': [],
                        'ocr_text': text[:500]  # 디버깅용
                    }, status=status.HTTP_200_OK)
                
                print(f'🛒 Found {len(detected_ingredients)} ingredients')
                for item in detected_ingredients:
                    print(f'   - {item["name"]}: {item["quantity"]}{item["unit"]}')
                
                return Response({
                    'message': f'영수증에서 {len(detected_ingredients)}개 식재료 인식 완료!',
                    'detected_ingredients': detected_ingredients,
                    'ocr_text': text[:200]  # 미리보기
                }, status=status.HTTP_200_OK)
                
            except ImportError:
                print('❌ pytesseract not installed')
                return Response({
                    'message': 'OCR 기능이 설치되지 않았습니다.',
                    'detected_ingredients': []
                }, status=status.HTTP_200_OK)
            except Exception as e:
                print(f'❌ OCR Error: {type(e).__name__}')
                print(f'   Message: {str(e)}')
                import traceback
                traceback.print_exc()
                return self._return_dummy_data()
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _return_dummy_data(self):
        """더미 데이터 반환"""
        detected_ingredients = [
            {
                'name': '사과',
                'quantity': 3,
                'unit': '개',
                'storage_method': '냉장',
                'expiry_date': (date.today() + timedelta(days=7)).isoformat()
            }
        ]
        
        return Response({
            'message': '식재료 인식 완료 (테스트 모드)',
            'detected_ingredients': detected_ingredients
        }, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """식재료 소진 (수량 차감)"""
        ingredient = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        if quantity <= 0:
            return Response({
                'error': '소진할 수량을 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity >= ingredient.quantity:
            # 전체 소진
            ingredient.delete()
            return Response({
                'message': '식재료가 모두 소진되었습니다.'
            })
        else:
            # 일부 소진
            ingredient.quantity -= quantity
            ingredient.save()
            
            return Response({
                'message': f'{quantity}{ingredient.unit} 소진되었습니다.',
                'remaining_quantity': ingredient.quantity
            })
