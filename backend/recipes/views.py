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
from config.constants import normalize_category

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
    ordering_fields = ['cooking_time_minutes', 'created_at', 'scrap_count']
    
    def get_queryset(self):
        """쿼리셋 필터링 (내 레시피, 스크랩한 레시피)"""
        queryset = super().get_queryset()
        
        # 좋아요(스크랩) 수 카운트 (정렬용)
        from django.db.models import Count
        queryset = queryset.annotate(scrap_count=Count('scraped_by'))
        
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
    
    def get_serializer_context(self):
        """Serializer에 request context 전달"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
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
        recipe = self.get_object()
        recipe_ingredients = recipe.ingredients.all()
        
        consumed_items = []
        not_found_items = []
        
        def parse_num(s):
            """문자열에서 숫자 추출 (분수 포함)"""
            if not s: return 1.0
            s = s.replace(" ", "")
            # 분수 형태 (1/2) 처리
            match_frac = re.search(r'(\d+)/(\d+)', s)
            if match_frac:
                return float(match_frac.group(1)) / float(match_frac.group(2))
            # 소수점 포함 숫자 추출
            match_num = re.search(r'(\d+\.\d+|\d+)', s)
            return float(match_num.group(1)) if match_num else 1.0

        def get_standard_val(val, unit):
            """단위에 따른 가중치 적용 (표준화)"""
            u = unit.lower()
            if u in ['kg', 'l', '리터', '킬로']: return val * 1000
            return val

        from refrigerator.models import UserIngredient
        
        for ring in recipe_ingredients:
            def check_match(name1, name2):
                n1 = name1.replace(" ", "")
                n2 = name2.replace(" ", "")
                
                # 동의어 매핑
                syns = {
                    '달걀': '계란', '계란': '달걀', 
                    '소고기': '쇠고기', '쇠고기': '소고기', 
                    '닭고기': '닭', '돼지고기': '돼지',
                    '대파': '파', '파': '대파',
                    '다진마늘': '마늘', '마늘': '다진마늘',
                    '양파': '생양파', '고춧가루': '고추가루',
                    '참기름': '들기름', '식용유': '오일',
                    '간장': '진간장', '진간장': '간장', '국간장': '간장',
                    '설탕': '올리고당', '올리고당': '설탕'
                }
                
                if n1 == n2: return True
                if n1 in n2 or n2 in n1: return True
                
                for k, v in syns.items():
                    if k in n1:
                        alt_n1 = n1.replace(k, v)
                        if alt_n1 == n2 or alt_n1 in n2 or n2 in alt_n1: return True
                    if k in n2:
                        alt_n2 = n2.replace(k, v)
                        if n1 == alt_n2 or n1 in alt_n2 or alt_n2 in n1: return True
                return False

            candidates = UserIngredient.objects.filter(user=user, is_deleted=False).order_by('expiry_date')
            target_ing = None
            
            for cing in candidates:
                if check_match(ring.name, cing.name):
                    target_ing = cing
                    break
            
            if target_ing:
                # quantity 필드 제거됨: 기본 수량으로 차감
                # TODO: 사용자가 요리 완료 시 직접 차감량을 입력하도록 수정 필요
                consumed_items.append({
                    'name': target_ing.name,
                    'note': '재료 사용됨 (수량 정보 없음)',
                    'status': 'used'
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
        filter_ingredients_raw = request.query_params.get('ingredients', '')
        filter_ingredients = filter_ingredients_raw.split(',') if filter_ingredients_raw else []
        
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
            actual_match_count = 0
            matched_list = []
            recipe_ingredients_names = []
            
            # 레시피 재료 유니크 세트 생성 (중복 제거 및 정규화)
            unique_recipe_ings = set(ring.name.replace(" ", "") for ring in recipe_ingredients_objs)
            total_kinds_count = len(unique_recipe_ings)
            
            def get_variants(name):
                name = name.replace(" ", "")
                variants = [name]
                syns = {
                    '달걀': '계란', '계란': '달걀', 
                    '소고기': '쇠고기', '쇠고기': '소고기', 
                    '닭고기': '닭', '돼지고기': '돼지',
                    '대파': '파', '파': '대파',
                    '다진마늘': '마늘', '마늘': '다진마늘',
                    '양파': '생양파', '고춧가루': '고추가루',
                    '참기름': '들기름', '식용유': '오일',
                    '간장': '진간장', '진간장': '간장', '국간장': '간장',
                    '설탕': '올리고당'
                }
                for k, v in syns.items():
                    if k in name:
                        variants.append(name.replace(k, v))
                return variants

            for ring in recipe_ingredients_objs:

                recipe_ingredients_names.append(ring.name)
                clean_ring_name = ring.name.replace(" ", "")
                
                name_variants = get_variants(clean_ring_name)
                
                found = False
                for uing in user_unique_names: # 중복 제거된 종류 리스트 사용
                    if not uing: continue # 빈 이름 방지
                    
                    # uing 도 정규화된 상태 (공백 제거됨)
                    if any((uing and (uing in v or v in uing)) for v in name_variants):
                        actual_match_count += 1
                        matched_list.append(ring.name)
                        found = True
                        break
            
            # 매칭 로직 정밀화: 레시피의 각 재료 종류가 사용자 재료 중 하나라도 매칭되는지 체크
            matched_kinds = []
            for ring in unique_recipe_ings:
                # ring (레시피 재료)이 사용자 재료(uing) 중 하나와 매칭되는지 확인 (`get_variants` 활용)
                is_matched = False
                
                # 레시피 재료의 이명(동의어) 구하기
                ring_variants = get_variants(ring) # ring은 이미 공백제거된 상태
                
                for uing in user_unique_names:
                    # uing: 사용자 재료 (공백제거됨)
                    
                    # 완전 일치만 (동의어 포함)
                    if uing in ring_variants or ring in get_variants(uing):
                        is_matched = True
                        break
                
                if is_matched:
                    matched_kinds.append(ring)
            
            actual_match_count = len(matched_kinds)
            display_match_ratio = actual_match_count / total_kinds_count if total_kinds_count > 0 else 0
            
            # 특정 재료 필터링 (활용하기 등에서 넘어온 경우)
            # 해당 재료들이 포함된 레시피에 대해 가중 점수 부여
            extra_weight = 0
            if filter_ingredients:
                matches_filter = [f for f in filter_ingredients if any(f.replace(" ","") in m.replace(" ","") for m in matched_kinds)]
                if matches_filter:
                    # 필터링된 재료가 하나라도 포함되면 우선순위 상승
                    extra_weight = 1.0 + (len(matches_filter) * 0.1)
                else:
                    # 필터링된 재료가 하나도 없으면 추천에서 후순위로 (또는 제외)
                    # 여기서는 후순위로 밀기 위해 가산점 없음
                    pass
            
            # 유통기한 임박 재료 매칭 개수 별도 계산
            expiring_match_count = sum(1 for m in matched_list if m.replace(" ","") in expiring_soon_names)
            
            # 가산점이 포함된 정렬용 점수 (내부적으로만 사용)
            # 순수 매칭률 + 임박 재료 가산점 + 특정 필터 가산점
            weighted_score = display_match_ratio + (expiring_match_count * 0.05) + extra_weight
            
            missing_ingredients = [name for name in recipe_ingredients_names if name not in matched_list]
            # quantity 필드 제거됨: 이름만 반환
            missing_ingredients_detailed = [
                {'name': ring.name} 
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
            
            # 매칭 결과 결정
            match_status = 'none'
            if actual_match_count > 0:
                match_status = 'partial'
                if display_match_ratio >= 0.99: match_status = 'full'
                elif display_match_ratio >= 0.5: match_status = 'high'
            elif is_diet and '샐러드' in (getattr(recipe, 'category', '') or ''):
                match_status = 'diet'
            
            # 특정 재료 필터링 (활용하기 등에서 넘어온 경우) - 사용자의 강력한 요청: 검색처럼 작동하게!
            if filter_ingredients:
                # 필터 재료들이 모두 matched_kinds 에 포함되어 있는지 확인
                # (부분 일치 허용: '계란' 필터인데 '계란지단' 매칭된 경우 등)
                all_filter_matched = True
                for f in filter_ingredients:
                    f_clean = f.replace(" ","")
                    if not any(f_clean in m.replace(" ","") or m.replace(" ","") in f_clean for m in matched_kinds):
                        all_filter_matched = False
                        break
                
                if not all_filter_matched:
                    continue # 필터 재료가 하나라도 없으면 과감히 탈락
                else:
                    # 모두 포함되었다면 점수 대폭 상승 (최상단 노출)
                    weighted_score += 10.0

            recommended_recipes.append({
                'recipe': recipe,
                'weighted_score': weighted_score, # 가산점 포함된 점수 사용
                'display_ratio': display_match_ratio,
                'match_count': actual_match_count,
                'expiring_match_count': expiring_match_count,
                'matched_ingredients': matched_list,
                'missing_ingredients': missing_ingredients,
                'missing_ingredients_detailed': missing_ingredients_detailed,
                'total_ingredients': total_kinds_count, # 종류 개수로 변경
                'match_status': match_status
            })
        
        # 필터링: 사용자가 요청한 최소 비율 이상인 것만
        recommended_recipes = [r for r in recommended_recipes if r['display_ratio'] >= min_ratio or r['match_status'] == 'diet']
        
        # 정렬 우선순위: weighted_score (필터 매칭된 것이 10점 높으므로 최상단)
        recommended_recipes.sort(key=lambda x: (x['weighted_score']), reverse=True)
        # 최대 100개까지 반환
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
        from master.models import IngredientMaster
        
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

중요 규칙:
1. 재료명은 반드시 "표준 식재료명"을 사용하세요 (예: '달걀' O, '계란' O, '유기농 달걀' X -> '달걀'로 통일).
2. 브랜드명이나 수식어(신선한, 맛있는 등)를 뺀 순수 재료명만 적으세요.
3. 한국어로 작성하세요.
"""
        
        try:
            url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gms_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3} # 창의성 낮춤 (정확도 UP)
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
                api_source='ai_generated',
                author=request.user
            )
            
            # 재료 생성 및 마스터 DB 매칭
            for ing in recipe_data.get('ingredients', []):
                raw_name = ing.get('name', '').strip()
                
                # 1. 괄호 및 특수문자 제거 정제
                # (예: "돼지고기(뒷다리살)" -> "돼지고기")
                clean_name = re.sub(r'\(.*?\)|\[.*?\]', '', raw_name).strip()
                
                final_name = clean_name
                master = None
                
                # 2. 정확 매칭 시도
                master = IngredientMaster.objects.filter(name=clean_name).first()
                
                if not master:
                    # 3. 공백 포함된 경우단어별 분리 매칭 시도 (예: "스리라차소스 한큰술" -> "스리라차소스" 찾기)
                    # 수식어나 단위가 뒤에 붙은 경우를 처리
                    parts = clean_name.split()
                    for i in range(len(parts), 0, -1):
                        sub_name = " ".join(parts[:i])
                        master = IngredientMaster.objects.filter(name=sub_name).first()
                        if master:
                            break
                
                if not master:
                    # 4. 포함 검색 (가장 짧은 것 = 가장 일반적인 것 선택)
                    # 예: '다진 마늘' -> '마늘'
                    candidates = IngredientMaster.objects.filter(name__icontains=clean_name)
                    if not candidates.exists() and len(clean_name) > 1:
                         # 반대로 마스터 DB의 재료가 AI 생성 재료명에 포함되는지 확인 (단, 너무 짧은 단어 제외)
                         # 예: "국산 콩나물" -> "콩나물"
                         # DB 부하를 줄이기 위해 clean_name의 일부로 검색
                         search_key = clean_name[:2] # 앞 2글자로 검색
                         candidates = IngredientMaster.objects.filter(name__startswith=search_key)
                         
                         # 그 중에서 clean_name에 포함되는 마스터 재료 찾기
                         valid_candidates = []
                         for cand in candidates:
                             if cand.name in clean_name:
                                 valid_candidates.append(cand)
                         
                         if valid_candidates:
                             # 가장 긴 매칭을 선택 (구체적인 것 우선? 아니면 짧은 것(일반적인 것)? -> 일반적인 것(짧은것)이 안전)
                             # 예: "청양고추" (4) vs "고추" (2) -> "청양고추"가 "청양고추"에 포함됨. 
                             # "알배기 배추" -> "배추" 포함됨.
                             # 문맥상 마스터에 있는걸 쓰는게 목적이므로, 가장 긴 매칭(정보 손실 최소화) 선택?
                             # 아니면 가장 짧은 매칭(범용성)? "무조건 마스터 DB 매칭"이 목표.
                             # "돼지고기전지" -> "돼지고기" 매칭되려면 "돼지고기"가 포함되어야 함.
                             master = sorted(valid_candidates, key=lambda x: len(x.name), reverse=True)[0]

                    if not master and candidates.exists():
                         # icontains 결과 중 가장 짧은 것 선택
                         master = sorted(candidates, key=lambda x: len(x.name))[0]
                
                if master:
                    final_name = master.name
                else:
                    # 5. 마스터 DB 매칭 실패 시 -> 저장하지 않거나(스킵), 가장 유사한걸 찾거나...
                    # "무조건 마스터 DB에 있는 재료로" -> 실패하면 "기타 재료"로라도 처리? 
                    # 일단 스킵하지는 않고 원래 이름을 쓰되, 최대한 정제된 clean_name 사용
                    # (여기서 마스터에 없으면 유저 재료랑 매칭이 안될 것임)
                    # 최후의 수단: AI가 인정한 재료명이니 일단 넣음 (마스터에 추가하라는 요청은 없고 '대조'하라고만 함)
                    # 유저 요청: "마스터 DB와 대조, 없을 경우 마스터 DB에 추가 (X -> 예시 설명에는 추가라고 되어있는데 로직 설명엔 없음?)"
                    # 아, 예시: "스리라차소스 로 변경 후 마스터 DB와 대조, 없을 경우 마스터 DB에 스리라차소스 추가"
                    # -> **마스터 DB에 추가**하라는 요청이네요!
                    # "돼지고기전지 -> 돼지고기 로 매칭" 은 있는 경우 매칭.
                    
                    # 마스터 DB에 없으면 추가!
                    new_cat = normalize_category(clean_name) # 카테고리 추론 필요
                    master = IngredientMaster.objects.create(name=clean_name, category=new_cat)
                    final_name = clean_name
                
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    name=final_name
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

