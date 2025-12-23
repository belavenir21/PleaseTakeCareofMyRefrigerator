from rest_framework import viewsets, filters, status
import re
import requests
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from django.conf import settings
from .models import Recipe, CookingStep, RecipeIngredient
from .serializers import (
    RecipeListSerializer, RecipeDetailSerializer, CookingStepSerializer, RecipeCreateSerializer
)
from refrigerator.models import UserIngredient

class RecipeFilter(django_filters.FilterSet):
    """레시피 필터"""
    difficulty = django_filters.CharFilter(field_name='difficulty')
    cooking_time_max = django_filters.NumberFilter(field_name='cooking_time_minutes', lookup_expr='lte')
    
    class Meta:
        model = Recipe
        fields = ['difficulty']

from config.authentication import CsrfExemptSessionAuthentication

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class RecipeViewSet(viewsets.ModelViewSet):
    """레시피 ViewSet (조회, 생성, 수정, 삭제 가능)"""
    queryset = Recipe.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser] # 이미지 업로드를 위해 필요
    filterset_class = RecipeFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'ingredients__name']
    ordering_fields = ['cooking_time_minutes', 'created_at']
    
    def get_queryset(self):
        """쿼리셋 필터링 (내 레시피, 스크랩한 레시피)"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # ?author=me : 내가 작성한 레시피
        author_param = self.request.query_params.get('author')
        if author_param == 'me' and user.is_authenticated:
            queryset = queryset.filter(author=user)
            
        # ?scraped=true : 내가 스크랩한 레시피
        scraped_param = self.request.query_params.get('scraped')
        if scraped_param == 'true' and user.is_authenticated:
            queryset = queryset.filter(scraped_by=user)
            
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeDetailSerializer
    
    @action(detail=True, methods=['get'])
    def steps(self, request, pk=None):
        """레시피의 조리 단계 조회 (요리 모드용)"""
        recipe = self.get_object()
        steps = recipe.steps.all()
        serializer = CookingStepSerializer(steps, many=True)
        
        return Response({
            'recipe_id': recipe.id,
            'recipe_title': recipe.title,
            'image_url': recipe.image_url,
            'total_steps': steps.count(),
            'total_time': recipe.cooking_time_minutes,
            'steps': serializer.data
        })

        
    @action(detail=True, methods=['post'])
    def scrap(self, request, pk=None):
        """레시피 스크랩 토글"""
        recipe = self.get_object()
        user = request.user
        
        if recipe.scraped_by.filter(id=user.id).exists():
            recipe.scraped_by.remove(user)
            scraped = False
            msg = "스크랩이 취소되었습니다."
        else:
            recipe.scraped_by.add(user)
            scraped = True
            msg = "레시피를 스크랩했습니다!"
            
        return Response({
            'scraped': scraped,
            'message': msg
        })
    @action(detail=True, methods=['post'])
    def complete_cooking(self, request, pk=None):
        """요리 완료 후 사용한 재료 자동 차감"""
        recipe = self.get_object()
        user = request.user
        recipe_ingredients = recipe.ingredients.all()
        
        consumed_items = []
        not_found_items = []
        
        from refrigerator.models import UserIngredient
        
        for ring in recipe_ingredients:
            # 1. 이름이 완전히 일치하거나 포함하는 재료 찾기 (가장 유통기한 임박한 것 우선)
            # 공백 제거 후 비교
            clean_ring_name = ring.name.replace(" ", "")
            
            candidates = UserIngredient.objects.filter(user=user).order_by('expiry_date')
            target_ing = None
            
            for cing in candidates:
                clean_cing_name = cing.name.replace(" ", "")
                if clean_ring_name in clean_cing_name or clean_cing_name in clean_ring_name:
                    target_ing = cing
                    break
            
            if target_ing:
                # 수량 및 단위 파싱
                recipe_qty_str = ring.quantity
                decrement = 1.0
                unit_matched = False
                
                # 1. 단위 매칭 확인 (g, ml, 개 등)
                if target_ing.unit in recipe_qty_str:
                    unit_matched = True
                
                # 2. 숫자 추출 (분수 포함: 1/2, 0.5 등)
                try:
                    # '1/2' 형태 처리
                    fraction_match = re.search(r'(\d+)\s*/\s*(\d+)', recipe_qty_str)
                    if fraction_match:
                        decrement = float(fraction_match.group(1)) / float(fraction_match.group(2))
                    else:
                        # 일반 숫자 추출
                        num_match = re.search(r'(\d+\.?\d*)', recipe_qty_str)
                        if num_match:
                            decrement = float(num_match.group(1))
                except:
                    decrement = 1.0
                
                # 단위가 다르면 (예: 레시피는 g, 나는 개) 
                # 정교한 환산 대신 일단 1개(단위)만 차감하거나 기본값 유지
                if not unit_matched:
                    # 무게 단위인데 개수 단위인 경우 등은 1로 고정 (안전빵)
                    if any(u in recipe_qty_str for u in ['g', 'ml', 'kg']) and target_ing.unit in ['개', '봉', '팩']:
                        decrement = 1.0
                
                if target_ing.quantity <= decrement:
                    actual_consumed = target_ing.quantity
                    target_ing.delete()
                    consumed_items.append({
                        'name': target_ing.name,
                        'consumed_quantity': f"{actual_consumed}{target_ing.unit}",
                        'status': 'finished'
                    })
                else:
                    target_ing.quantity -= decrement
                    target_ing.save()
                    consumed_items.append({
                        'name': target_ing.name,
                        'consumed_quantity': f"{decrement}{target_ing.unit}",
                        'status': 'reduced',
                        'remaining': f"{target_ing.quantity}{target_ing.unit}"
                    })
            else:
                not_found_items.append(ring.name)
        
        return Response({
            'message': f'"{recipe.title}" 요리 완료! 재료가 정리되었습니다.',
            'consumed': consumed_items,
            'not_found': not_found_items
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """맞춤 레시피 추천 (취향 및 냉장고 재료 반영)"""
        user = request.user
        profile = getattr(user, 'profile', None)
        diet_goals = profile.diet_goals if profile else ""
        
        # 필터 정보
        min_ratio = float(request.query_params.get('min_ratio', 0.1)) # 기본값 10%로 완화
        
        # 알레르기 정보 가져오기
        user_allergy_names = []
        forbidden_ingredients = []
        if profile:
            user_allergies = profile.allergies.all()
            user_allergy_names = [a.name for a in user_allergies]
            
            # 알레르기 유발 마스터 재료들 찾기
            from master.models import IngredientMaster
            forbidden_masters = IngredientMaster.objects.filter(allergies__in=user_allergies)
            forbidden_ingredients = [m.name for m in forbidden_masters]

        # 1. 사용자의 보관 중인 식재료 가져오기 (이름과 유통기한 정보를 함께 가져옴)
        from django.db.models import Case, When, Value, FloatField
        from datetime import date, timedelta
        
        user_ings = UserIngredient.objects.filter(user=user)
        user_ingredients_list = []
        user_unique_names = set() # 종류를 세기 위한 세트
        expiring_soon_names = []
        
        today = date.today()
        soon_date = today + timedelta(days=3)
        
        for ui in user_ings:
            clean_name = ui.name.replace(" ", "")
            user_ingredients_list.append(clean_name)
            user_unique_names.add(clean_name) # 종류 추가
            # 유통기한이 3일 이내인 재료들 메모
            if ui.expiry_date <= soon_date:
                expiring_soon_names.append(clean_name)
                
        user_ingredients_count = len(user_unique_names) # 중복 제외한 '종류'의 개수
        
        # 2. 레시피 데이터 가져오기 (재료 정보를 한꺼번에 가져옴)
        all_recipes = Recipe.objects.all().prefetch_related('ingredients')
        
        # 채식주의자 필터링 예시
        diet_goals_str = diet_goals or ''
        is_vegetarian = '#채식' in diet_goals_str
        is_diet = '#다이어트' in diet_goals_str
        
        meat_keywords = ['소고기', '돼지고기', '닭고기', '베이컨', '햄', '소시지', '육류', '오리고기', '계란']
        
        recommended_recipes = []
        
        for recipe in all_recipes:
            recipe_ingredients_objs = recipe.ingredients.all()
            if not recipe_ingredients_objs:
                continue
                
            match_count = 0
            matched_list = []
            recipe_ingredients_names = []
            
            for ring in recipe_ingredients_objs:
                recipe_ingredients_names.append(ring.name)
                clean_ring_name = ring.name.replace(" ", "")
                
                # 동의어 및 정규화 처리
                def get_variants(name):
                    name = name.replace(" ", "")
                    variants = [name]
                    syns = {'달걀': '계란', '계란': '달걀', '소고기': '쇠고기', '쇠고기': '소고기', '닭고기': '닭', '돼지고기': '돼지'}
                    for k, v in syns.items():
                        if k in name: variants.append(name.replace(k, v))
                    return variants

                name_variants = get_variants(clean_ring_name)
                
                found = False
                for uing in user_ingredients_list:
                    # uing 도 정규화된 상태 (공백 제거됨)
                    if any(uing in v or v in uing for v in name_variants):
                        match_count += 1
                        matched_list.append(ring.name)
                        if any(uing in esn for esn in expiring_soon_names):
                            match_count += 0.5
                        found = True
                        break
            
            total_count = len(recipe_ingredients_names)
            # 순수 매칭 개수
            actual_match_count = len(matched_list)
            
            # 가산점이 포함된 매칭 점수 (정렬용)
            # 재료 개수 비중을 높이고, 유통기한 임박은 보너스 점수로 처리
            # 예: 10개 중 4개 매칭이면 40점 + 보너스
            weighted_score = actual_match_count
            for m in matched_list:
                if m.replace(" ","") in expiring_soon_names:
                    weighted_score += 0.1 # 보너스 점수를 작게 조정하여 비율을 해치지 않게 함
            
            # 실제 화면에 보여줄 매칭 비율 (수학적으로 정확하게)
            display_match_ratio = actual_match_count / total_count if total_count > 0 else 0
            
            missing_ingredients = [name for name in recipe_ingredients_names if name not in matched_list]
            missing_ingredients_detailed = [
                {'name': ring.name, 'quantity': ring.quantity} 
                for ring in recipe_ingredients_objs if ring.name not in matched_list
            ]
            
            # 취향 필터링: 채식인데 고기가 들어가면 탈락
            if is_vegetarian:
                if any(meat in name for name in recipe_ingredients_names for meat in meat_keywords):
                    continue
            
            # 알레르기 필터링
            has_allergy = False
            for ring_name in recipe_ingredients_names:
                if any(forbidden in ring_name or ring_name in forbidden for forbidden in forbidden_ingredients):
                    has_allergy = True; break
                if any(allergy in ring_name for allergy in user_allergy_names):
                    has_allergy = True; break
            if has_allergy: continue
            
            # 최소 1개라도 매칭되거나, 다이어트용 샐러드인 경우 추천
            # 조건 완화: 매칭이 0개여도 일단 목록에 추가 (정렬로 우선순위 결정)
            # 매칭 결과 결정
            match_status = 'none'
            if actual_match_count > 0:
                match_status = 'partial'
                if display_match_ratio >= 0.8: match_status = 'full'
                elif display_match_ratio >= 0.5: match_status = 'high'
            elif is_diet and '샐러드' in (getattr(recipe, 'category', '') or ''):
                match_status = 'diet'
                
            # 유통기한 임박 재료 매칭 개수 별도 계산
            expiring_match_count = sum(1 for m in matched_list if m.replace(" ","") in expiring_soon_names)
            
            recommended_recipes.append({
                'recipe': recipe,
                'weighted_score': weighted_score,
                'display_ratio': display_match_ratio,
                'match_count': actual_match_count,
                'expiring_match_count': expiring_match_count,  # 추가
                'matched_ingredients': matched_list,
                'missing_ingredients': missing_ingredients,
                'missing_ingredients_detailed': missing_ingredients_detailed,
                'total_ingredients': total_count,
                'match_status': match_status
            })
        
        # 필터링: 사용자가 요청한 최소 비율 이상인 것만
        recommended_recipes = [r for r in recommended_recipes if r['display_ratio'] >= min_ratio or r['match_status'] == 'diet']
        
        # 정렬 우선순위 변경:
        # 1. 유통기한 임박 재료 매칭 개수 (가장 중요!)
        # 2. 전체 매칭 개수
        # 3. 매칭 비율
        recommended_recipes.sort(key=lambda x: (x['expiring_match_count'], x['match_count'], x['display_ratio']), reverse=True)
        # 최대 100개까지 반환 (사용자가 더 많이 보길 원하므로 늘림)
        recommended_recipes = recommended_recipes[:100]
        
        recipes_data = []
        for item in recommended_recipes:
            recipe_data = RecipeListSerializer(item['recipe']).data
            recipe_data['match_ratio'] = round(item['display_ratio'] * 100, 0) # 정수로 깔끔하게 표시
            recipe_data['match_count'] = item['match_count']
            recipe_data['missing_ingredients'] = item['missing_ingredients']
            recipe_data['missing_ingredients_detailed'] = item['missing_ingredients_detailed']
            recipe_data['total_ingredients'] = item['total_ingredients']
            recipe_data['match_status'] = item['match_status']
            # 사용 중인 임박 재료가 있는지 표시
            recipe_data['uses_expiring_ingredients'] = any(m.replace(" ","") in expiring_soon_names for m in item['matched_ingredients'])
            recipes_data.append(recipe_data)
        
        print(f"[REC-DEBUG] Recommended: {len(recipes_data)} recipes for user {user.username} (Has {user_ingredients_count} ingredients)")
        
        return Response({
            'count': len(recipes_data),
            'recipes': recipes_data,
            'user_ingredient_count': user_ingredients_count,
            'applied_filters': {
                'vegetarian': is_vegetarian,
                'diet': is_diet,
                'allergies': user_allergy_names
            }
        })
    
    @action(detail=False, methods=['post'])
    def create_recipe(self, request):
        """사용자 레시피 직접 등록"""
        serializer = RecipeCreateSerializer(data=request.data)
        if serializer.is_valid():
            recipe = serializer.save()
            return Response({
                'message': f'레시피 "{recipe.title}"가 등록되었습니다!',
                'recipe': RecipeDetailSerializer(recipe).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def generate_recipe(self, request):
        """AI로 레시피 자동 생성"""
        recipe_name = request.data.get('recipe_name', '')
        
        if not recipe_name:
            return Response({'error': '레시피 이름을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        gms_key = getattr(settings, 'GMS_KEY', None)
        if not gms_key:
            return Response({'error': 'AI 서비스가 설정되지 않았습니다.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        prompt = f"""
당신은 요리 전문가입니다. "{recipe_name}" 레시피를 JSON 형식으로 생성해주세요.

반드시 아래 형식으로 응답하세요 (코드블록 없이 순수 JSON만):
{{
    "title": "레시피 제목",
    "description": "레시피 설명 (2-3문장)",
    "cooking_time_minutes": 조리시간(숫자),
    "difficulty": "쉬움/보통/어려움 중 하나",
    "category": "한식/양식/중식/일식/디저트/샐러드/기타 중 하나",
    "tags": ["태그1", "태그2"],
    "ingredients": [
        {{"name": "재료명", "quantity": "수량 (예: 200g, 2개)"}},
        ...
    ],
    "steps": [
        {{"description": "조리 단계 설명", "time_minutes": 소요시간(숫자)}},
        ...
    ]
}}

중요:
- 재료는 실제 필요한 것만 포함
- 조리 단계는 상세하게 5-8단계 정도
- 한국어로 작성
"""
        
        try:
            url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gms_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7}
            }
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code != 200:
                error_detail = response.text[:500] if response.text else 'No response body'
                print(f"[AI-RECIPE-ERROR] Status: {response.status_code}, Detail: {error_detail}")
                return Response({
                    'error': f'AI 응답 오류 (Status: {response.status_code})',
                    'detail': error_detail
                }, status=status.HTTP_502_BAD_GATEWAY)
            
            result = response.json()
            ai_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            # JSON 파싱
            import json
            # 코드블록 제거
            ai_text = ai_text.strip()
            if ai_text.startswith('```'):
                ai_text = ai_text.split('```')[1]
                if ai_text.startswith('json'):
                    ai_text = ai_text[4:]
            if ai_text.endswith('```'):
                ai_text = ai_text[:-3]
            
            recipe_data = json.loads(ai_text.strip())
            
            # 레시피 생성
            recipe = Recipe.objects.create(
                title=recipe_data.get('title', recipe_name),
                description=recipe_data.get('description', ''),
                cooking_time_minutes=recipe_data.get('cooking_time_minutes', 30),
                difficulty=recipe_data.get('difficulty', '보통'),
                category=recipe_data.get('category', '기타'),
                tags=recipe_data.get('tags', []),
                api_source='ai_generated'
            )
            
            # 재료 생성
            for ing in recipe_data.get('ingredients', []):
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    name=ing.get('name', ''),
                    quantity=ing.get('quantity', '')
                )
            
            # 조리 단계 생성
            for idx, step in enumerate(recipe_data.get('steps', []), 1):
                CookingStep.objects.create(
                    recipe=recipe,
                    step_number=idx,
                    description=step.get('description', ''),
                    time_minutes=step.get('time_minutes', 0),
                    icon='🍳'
                )
            
            return Response({
                'message': f'AI가 "{recipe.title}" 레시피를 생성했습니다!',
                'recipe': RecipeDetailSerializer(recipe).data
            }, status=status.HTTP_201_CREATED)
            
        except json.JSONDecodeError as e:
            return Response({
                'error': 'AI 응답 파싱 실패',
                'raw_response': ai_text[:500]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'레시피 생성 실패: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

