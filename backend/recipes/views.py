"""
레시피 Views - V2
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters import rest_framework as django_filters
from django.db.models import Count

from .models import Recipe, RecipeIngredient, CookingStep
from .serializers import (
    RecipeListSerializer,
    RecipeDetailSerializer,
    CookingStepSerializer,
    RecipeCreateSerializer
)
from refrigerator.models import UserIngredient
from master.models import IngredientMaster, IngredientSynonym, find_master_by_name
from config.authentication import CsrfExemptSessionAuthentication


class RecipeFilter(django_filters.FilterSet):
    """레시피 필터"""
    difficulty = django_filters.CharFilter(field_name='difficulty')
    cooking_time_max = django_filters.NumberFilter(field_name='cooking_time', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category')
    source = django_filters.CharFilter(field_name='source')

    class Meta:
        model = Recipe
        fields = ['difficulty', 'category', 'source']


class RecipeViewSet(viewsets.ModelViewSet):
    """레시피 ViewSet"""
    queryset = Recipe.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = RecipeFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'ingredients__name']
    ordering_fields = ['created_at', 'cooking_time', 'title']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_public=True)
        
        # 내 레시피만 보기
        filter_type = self.request.query_params.get('filter')
        if filter_type == 'my' and self.request.user.is_authenticated:
            queryset = Recipe.objects.filter(author=self.request.user)
        elif filter_type == 'scraped' and self.request.user.is_authenticated:
            queryset = self.request.user.scraped_recipes.all()
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action in ['create', 'create_recipe']:
            return RecipeCreateSerializer
        return RecipeListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'steps']:
            return [AllowAny()]
        return [IsAuthenticated()]

    # ===== 조리 단계 =====

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def steps(self, request, pk=None):
        """레시피 조리 단계 조회"""
        recipe = self.get_object()
        steps = recipe.steps.order_by('step_number')
        serializer = CookingStepSerializer(steps, many=True)
        return Response({
            'recipe_id': recipe.id,
            'recipe_title': recipe.title,
            'steps': serializer.data
        })

    # ===== 스크랩 =====

    @action(detail=True, methods=['post'])
    def scrap(self, request, pk=None):
        """레시피 스크랩 토글"""
        recipe = self.get_object()
        user = request.user
        
        if recipe.scraped_by.filter(id=user.id).exists():
            recipe.scraped_by.remove(user)
            return Response({'status': 'unscrapped', 'scraped': False})
        else:
            recipe.scraped_by.add(user)
            return Response({'status': 'scrapped', 'scraped': True})

    # ===== 요리 완료 =====

    @action(detail=True, methods=['post'])
    def complete_cooking(self, request, pk=None):
        """요리 완료 후 재료 차감"""
        recipe = self.get_object()
        user = request.user
        
        # 레시피 재료 목록
        recipe_ingredients = recipe.ingredients.all()
        
        # 사용자 보관함 재료
        user_ingredients = UserIngredient.objects.filter(user=user, is_deleted=False)
        
        consumed = []
        
        for ri in recipe_ingredients:
            # 마스터 기반 매칭 또는 이름 매칭
            matched = None
            
            if ri.master:
                matched = user_ingredients.filter(master=ri.master).first()
            
            if not matched:
                # 이름으로 매칭 (동의어 포함)
                master = find_master_by_name(ri.name)
                if master:
                    matched = user_ingredients.filter(master=master).first()
                else:
                    matched = user_ingredients.filter(name__icontains=ri.name).first()
            
            if matched:
                # 수량 차감 (기본 1개)
                if matched.quantity <= 1:
                    matched.is_deleted = True
                    matched.save()
                else:
                    matched.quantity -= 1
                    matched.save()
                consumed.append(matched.name)
        
        return Response({
            'message': f'{len(consumed)}개 재료가 차감되었습니다.',
            'consumed': consumed
        })

    # ===== 레시피 추천 =====

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """맞춤 레시피 추천 (냉장고 재료 기반)"""
        user = request.user
        
        # 사용자 보관함 재료 목록
        user_ingredients = UserIngredient.objects.filter(user=user, is_deleted=False)
        user_master_ids = set(ui.master_id for ui in user_ingredients if ui.master_id)
        user_names = set(ui.name for ui in user_ingredients)
        
        # 동의어 확장
        synonyms = IngredientSynonym.objects.filter(master_id__in=user_master_ids)
        synonym_names = set(s.synonym for s in synonyms)
        
        # 모든 매칭 가능한 이름
        all_user_names = user_names | synonym_names | set(
            m.name for m in IngredientMaster.objects.filter(id__in=user_master_ids)
        )
        
        # 레시피 필터링 및 매칭률 계산
        recipes = Recipe.objects.filter(is_public=True).prefetch_related('ingredients', 'ingredients__master')
        
        recommendations = []
        
        for recipe in recipes:
            recipe_ingredients = recipe.ingredients.all()
            total_count = recipe_ingredients.count()
            
            if total_count == 0:
                continue
            
            # 매칭된 재료 수 계산
            matched_count = 0
            for ri in recipe_ingredients:
                # 마스터 ID로 매칭
                if ri.master_id and ri.master_id in user_master_ids:
                    matched_count += 1
                # 이름으로 매칭
                elif ri.name in all_user_names:
                    matched_count += 1
                # 부분 매칭
                elif any(name in ri.name or ri.name in name for name in user_names):
                    matched_count += 1
            
            match_ratio = matched_count / total_count if total_count > 0 else 0
            
            # 1개 이상 매칭되면 추가
            if matched_count >= 1:
                recommendations.append({
                    'recipe': recipe,
                    'match_ratio': match_ratio,
                    'matched_count': matched_count,
                    'total_count': total_count
                })
        
        # 매칭률 순으로 정렬
        recommendations.sort(key=lambda x: x['match_ratio'], reverse=True)
        
        # 50% 이상과 미만으로 분리
        high_match = [r for r in recommendations if r['match_ratio'] >= 0.5][:20]
        low_match = [r for r in recommendations if r['match_ratio'] < 0.5][:30]
        
        def serialize_recipes(items):
            results = []
            for item in items:
                recipe_data = RecipeListSerializer(
                    item['recipe'],
                    context={'request': request}
                ).data
                recipe_data['match_ratio'] = round(item['match_ratio'] * 100, 1)
                recipe_data['matched_count'] = item['matched_count']
                recipe_data['total_ingredients'] = item['total_count']
                results.append(recipe_data)
            return results
        
        return Response({
            'count': len(high_match),
            'total_available': len(recommendations),
            'user_ingredients_count': len(user_names),
            'results': serialize_recipes(high_match),  # 50% 이상 (기본 표시)
            'more_recipes': serialize_recipes(low_match),  # 50% 미만 (더보기 클릭시)
            'has_more': len(low_match) > 0
        })

    # ===== 레시피 생성 =====

    @action(detail=False, methods=['post'])
    def create_recipe(self, request):
        """사용자 레시피 직접 등록"""
        serializer = RecipeCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            recipe = serializer.save()
            return Response(
                RecipeDetailSerializer(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def generate_recipe(self, request):
        """AI로 레시피 자동 생성"""
        from .ai_services import generate_recipe_with_ai
        
        recipe_name = request.data.get('recipe_name', '')
        if not recipe_name:
            return Response({'error': '레시피 이름이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recipe = generate_recipe_with_ai(recipe_name, request.user)
            return Response(
                RecipeDetailSerializer(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            error_msg = str(e)
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "API 키" in error_msg or "한도" in error_msg or "토큰" in error_msg else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({'error': error_msg}, status=status_code)
