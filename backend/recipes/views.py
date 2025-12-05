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

class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """레시피 ViewSet"""
    queryset = Recipe.objects.all()
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
        """맞춤 레시피 추천"""
        user = request.user
        
        # 사용자의 보관 중인 식재료 가져오기
        user_ingredients = UserIngredient.objects.filter(user=user).values_list('name', flat=True)
        user_ingredients_set = set(user_ingredients)
        
        # 레시피 중 사용자가 가진 재료로 만들 수 있는 것 찾기
        all_recipes = Recipe.objects.all()
        recommended_recipes = []
        
        for recipe in all_recipes:
            recipe_ingredients = set(recipe.ingredients.values_list('name', flat=True))
            
            # 보유 재료와 매칭 비율 계산
            if recipe_ingredients:
                match_count = len(recipe_ingredients & user_ingredients_set)
                match_ratio = match_count / len(recipe_ingredients)
                
                if match_ratio >= 0.5:  # 50% 이상 매칭
                    recommended_recipes.append({
                        'recipe': recipe,
                        'match_ratio': match_ratio,
                        'match_count': match_count,
                        'total_ingredients': len(recipe_ingredients)
                    })
        
        # 매칭 비율 순으로 정렬
        recommended_recipes.sort(key=lambda x: x['match_ratio'], reverse=True)
        
        # 최대 10개까지 추천
        recommended_recipes = recommended_recipes[:10]
        
        # Serialize
        recipes_data = []
        for item in recommended_recipes:
            recipe_data = RecipeListSerializer(item['recipe']).data
            recipe_data['match_ratio'] = round(item['match_ratio'] * 100, 1)
            recipe_data['match_count'] = item['match_count']
            recipe_data['total_ingredients'] = item['total_ingredients']
            recipes_data.append(recipe_data)
        
        return Response({
            'count': len(recipes_data),
            'recipes': recipes_data
        })
