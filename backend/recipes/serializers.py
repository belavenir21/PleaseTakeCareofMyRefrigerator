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


class RecipeCreateSerializer(serializers.ModelSerializer):
    """레시피 생성용 Serializer"""
    ingredients = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True,
        help_text="재료 목록 [{'name': '재료명', 'quantity': '수량'}]"
    )
    steps = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True, 
        required=False,
        help_text="조리 단계 [{'description': '설명', 'time_minutes': 5}]"
    )
    
    class Meta:
        model = Recipe
        fields = [
            'title', 'description', 'cooking_time_minutes',
            'difficulty', 'image_url', 'tags', 'category',
            'ingredients', 'steps'
        ]
    
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        steps_data = validated_data.pop('steps', [])
        
        # 사용자 레시피로 표시
        validated_data['api_source'] = 'user'
        
        recipe = Recipe.objects.create(**validated_data)
        
        # 재료 생성
        for ing in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=ing.get('name', ''),
                quantity=ing.get('quantity', '')
            )
        
        # 조리 단계 생성
        for idx, step in enumerate(steps_data, 1):
            CookingStep.objects.create(
                recipe=recipe,
                step_number=idx,
                description=step.get('description', ''),
                time_minutes=step.get('time_minutes', 0),
                icon=step.get('icon', '🍳')
            )
        
        return recipe

