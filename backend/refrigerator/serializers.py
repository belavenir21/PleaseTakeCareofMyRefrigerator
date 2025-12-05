from rest_framework import serializers
from .models import UserIngredient

class UserIngredientSerializer(serializers.ModelSerializer):
    """사용자 식재료 Serializer"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'storage_method', 
            'expiry_date', 'image', 'created_at', 'updated_at',
            'is_expiring_soon', 'is_expired', 'category'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_category(self, obj):
        if obj.master_ingredient:
            return obj.master_ingredient.category
        # 마스터 데이터가 연결 안 되어 있으면 이름으로 찾기
        from master.models import IngredientMaster
        # 이름에 포함된 키워드로 찾기 (간단하게)
        master = IngredientMaster.objects.filter(name=obj.name).first()
        if master:
            return master.category
        return '기타'

    def create(self, validated_data):
        # 사용자 정보 자동 설정
        validated_data['user'] = self.context['request'].user
        
        # 마스터 데이터 자동 연결 시도
        from master.models import IngredientMaster
        name = validated_data.get('name')
        if name:
            master = IngredientMaster.objects.filter(name=name).first()
            if master:
                validated_data['master_ingredient'] = master
                
        return super().create(validated_data)

class UserIngredientListSerializer(serializers.ModelSerializer):
    """식재료 목록 조회용 (간단한 정보만)"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'expiry_date',
            'is_expiring_soon', 'is_expired'
        ]

class IngredientScanSerializer(serializers.Serializer):
    """사진 스캔을 통한 식재료 등록"""
    image = serializers.ImageField()
    
class IngredientBulkCreateSerializer(serializers.Serializer):
    """여러 식재료 일괄 등록"""
    ingredients = UserIngredientSerializer(many=True)
    
    def create(self, validated_data):
        ingredients_data = validated_data['ingredients']
        user = self.context['request'].user
        
        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_data['user'] = user
            ingredient = UserIngredient.objects.create(**ingredient_data)
            ingredients.append(ingredient)
        
        return {'ingredients': ingredients}
