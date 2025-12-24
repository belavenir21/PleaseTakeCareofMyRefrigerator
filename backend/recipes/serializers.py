from rest_framework import serializers
from .models import Recipe, RecipeIngredient, CookingStep

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """레시피 재료 Serializer (quantity 필드 제거)"""
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name']

class CookingStepSerializer(serializers.ModelSerializer):
    """조리 단계 Serializer"""
    class Meta:
        model = CookingStep
        fields = ['id', 'step_number', 'description', 'icon', 'time_minutes']

class RecipeListSerializer(serializers.ModelSerializer):
    """레시피 목록 Serializer"""
    ingredients_count = serializers.SerializerMethodField()
    steps_count = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()
    is_scraped = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'cooking_time_minutes', 'difficulty',
            'image_url', 'image', 'tags', 'ingredients_count', 'steps_count', 'ingredients', 'author', 'is_scraped'
        ]
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.image_url

    def get_ingredients_count(self, obj):
        return obj.ingredients.count()
    
    def get_steps_count(self, obj):
        return obj.steps.count()
    
    def get_author(self, obj):
        """작성자 닉네임 반환 (안전하게)"""
        if obj.author:
            if hasattr(obj.author, 'profile') and obj.author.profile:
                return obj.author.profile.nickname or obj.author.username
            return obj.author.username
        return None
        
    def get_is_scraped(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.scraped_by.filter(id=request.user.id).exists()
        return False

class RecipeDetailSerializer(serializers.ModelSerializer):
    """레시피 상세 Serializer"""
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    steps = CookingStepSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()
    is_scraped = serializers.SerializerMethodField()
    scraped_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'cooking_time_minutes',
            'difficulty', 'image_url', 'image', 'tags', 'ingredients', 'steps',
            'created_at', 'updated_at', 'author', 'is_scraped', 'scraped_count'
        ]
        
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.image_url
    
    def get_author(self, obj):
        """작성자 닉네임 반환 (안전하게)"""
        if obj.author:
            if hasattr(obj.author, 'profile') and obj.author.profile:
                return obj.author.profile.nickname or obj.author.username
            return obj.author.username
        return None
        
    def get_is_scraped(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.scraped_by.filter(id=request.user.id).exists()
        return False
    
    def get_scraped_count(self, obj):
        """즐겨찾기한 사람 수"""
        return obj.scraped_by.count()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """레시피 생성용 Serializer"""
    ingredients = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True,
        required=False
    )
    steps = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True, 
        required=False
    )
    image = serializers.ImageField(required=False) # 이미지 업로드
    
    class Meta:
        model = Recipe
        fields = [
            'title', 'description', 'cooking_time_minutes',
            'difficulty', 'image_url', 'image', 'tags', 'category',
            'ingredients', 'steps'
        ]
    
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        steps_data = validated_data.pop('steps', [])
        
        validated_data['api_source'] = 'user'
        
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['author'] = request.user
        
        recipe = Recipe.objects.create(**validated_data)
        
        for ing in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=ing.get('name', '')
                # quantity 필드 제거됨
            )
        
        for idx, step in enumerate(steps_data, 1):
            CookingStep.objects.create(
                recipe=recipe,
                step_number=idx,
                description=step.get('description', ''),
                time_minutes=step.get('time_minutes', 0),
                icon=step.get('icon', '🍳')
            )
        
        return recipe

