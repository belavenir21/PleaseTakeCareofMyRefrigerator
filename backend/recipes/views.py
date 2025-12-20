from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from .models import Recipe, CookingStep
from .serializers import (
    RecipeListSerializer, RecipeDetailSerializer, CookingStepSerializer
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

class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """레시피 ViewSet"""
    queryset = Recipe.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = RecipeFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['cooking_time_minutes', 'created_at']
    
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
            'total_steps': steps.count(),
            'total_time': recipe.cooking_time_minutes,
            'steps': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """맞춤 레시피 추천 (취향 및 냉장고 재료 반영)"""
        user = request.user
        profile = getattr(user, 'profile', None)
        diet_goals = profile.diet_goals if profile else ""
        
        # 1. 사용자의 보관 중인 식재료 가져오기
        user_ingredients = UserIngredient.objects.filter(user=user).values_list('name', flat=True)
        # 검색 효율을 위해 정규화 (공백 제거 등)
        user_ingredients_list = [name.replace(" ", "") for name in user_ingredients]
        user_ingredients_count = len(user_ingredients_list)
        
        # 2. 레시피 필터링 (취향 반영)
        all_recipes = Recipe.objects.all().prefetch_related('ingredients')
        
        # 채식주의자 필터링 예시
        is_vegetarian = '#채식' in diet_goals
        is_diet = '#다이어트' in diet_goals
        
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
                # 유연한 매칭 로직: 레시피 재료명이 사용자 재료명에 포함되거나 그 반대인 경우
                clean_ring_name = ring.name.replace(" ", "")
                found = False
                for uing in user_ingredients_list:
                    if uing in clean_ring_name or clean_ring_name in uing:
                        match_count += 1
                        matched_list.append(ring.name)
                        found = True
                        break
            
            total_count = len(recipe_ingredients_names)
            match_ratio = match_count / total_count if total_count > 0 else 0
            missing_ingredients = [name for name in recipe_ingredients_names if name not in matched_list]
            
            # 취향 필터링: 채식인데 고기가 들어가면 탈락
            if is_vegetarian:
                if any(meat in name for name in recipe_ingredients_names for meat in meat_keywords):
                    continue
            
            # 10% 이상 매칭되거나, 모든 재료가 다 있거나, 특정 카테고리인 경우 포함
            if match_count > 0 or (is_diet and '샐러드' in recipe.category):
                match_status = 'partial'
                if match_ratio >= 0.8: match_status = 'full'
                elif match_ratio >= 0.4: match_status = 'high'
                
                recommended_recipes.append({
                    'recipe': recipe,
                    'match_ratio': match_ratio,
                    'match_count': match_count,
                    'matched_ingredients': matched_list,
                    'missing_ingredients': missing_ingredients[:5],
                    'total_ingredients': total_count,
                    'match_status': match_status
                })
        
        # 매칭 비율 순으로 정렬
        recommended_recipes.sort(key=lambda x: (x['match_ratio'], x['total_ingredients']), reverse=True)
        
        # 최대 20개까지 추천 (더 많은 옵션 제공)
        recommended_recipes = recommended_recipes[:20]
        
        # Serialize
        recipes_data = []
        for item in recommended_recipes:
            recipe_data = RecipeListSerializer(item['recipe']).data
            recipe_data['match_ratio'] = round(item['match_ratio'] * 100, 1)
            recipe_data['match_count'] = item['match_count']
            recipe_data['missing_ingredients'] = item['missing_ingredients']
            recipe_data['total_ingredients'] = item['total_ingredients']
            recipe_data['match_status'] = item['match_status']
            recipes_data.append(recipe_data)
        
        print(f"[REC-DEBUG] Recommended: {len(recipes_data)} recipes for user {user.username} (Has {user_ingredients_count} ingredients)")
        
        return Response({
            'count': len(recipes_data),
            'recipes': recipes_data,
            'user_ingredient_count': user_ingredients_count,
            'applied_filters': {
                'vegetarian': is_vegetarian,
                'diet': is_diet
            }
        })
