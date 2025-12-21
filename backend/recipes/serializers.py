from rest_framework import serializers
from .models import Recipe, RecipeIngredient, CookingStep

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """레시피 재료 Serializer"""
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'quantity']

class CookingStepSerializer(serializers.ModelSerializer):
    """조리 단계 Serializer"""
    class Meta:
        model = CookingStep
        fields = ['id', 'step_number', 'description', 'icon', 'time_minutes']

class RecipeListSerializer(serializers.ModelSerializer):
    """레시피 목록 Serializer (간단한 정보)"""
    ingredients_count = serializers.SerializerMethodField()
    steps_count = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'cooking_time_minutes', 'difficulty',
            'image_url', 'tags', 'ingredients_count', 'steps_count', 'ingredients'
        ]
    
    def get_ingredients_count(self, obj):
        return obj.ingredients.count()
    
    def get_steps_count(self, obj):
        return obj.steps.count()

class RecipeDetailSerializer(serializers.ModelSerializer):
    """레시피 상세 Serializer"""
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    steps = CookingStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'cooking_time_minutes',
            'difficulty', 'image_url', 'tags', 'ingredients', 'steps',
            'created_at', 'updated_at'
        ]
