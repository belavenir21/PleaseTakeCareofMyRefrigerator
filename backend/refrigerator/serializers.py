from rest_framework import serializers
from .models import UserIngredient

class UserIngredientSerializer(serializers.ModelSerializer):
    """사용자 식재료 Serializer"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    # category는 모델 필드를 그대로 사용 (쓰기 가능)
    icon = serializers.SerializerMethodField()
    
    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'storage_method', 
            'expiry_date', 'image', 'created_at', 'updated_at',
            'is_expiring_soon', 'is_expired', 'category', 'icon'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'category': {'required': False, 'allow_null': True, 'allow_blank': True}
        }
    
    def get_icon(self, obj):
        """재료의 아이콘을 반환 (개선된 매칭)"""
        # 1. master_ingredient가 직접 연결되어 있는 경우
        if obj.master_ingredient and obj.master_ingredient.icon:
            return obj.master_ingredient.icon
        
        # 2. 이름으로 마스터 데이터 검색
        from master.models import IngredientMaster
        master = IngredientMaster.objects.filter(name=obj.name).first()
        if master and master.icon:
            return master.icon
        
        # 3. 대소문자 무시하고 검색
        master = IngredientMaster.objects.filter(name__iexact=obj.name).first()
        if master and master.icon:
            return master.icon
        
        # 4. 카테고리 기반 기본 아이콘
        # 사용자가 설정한 카테고리가 있으면 사용, 없으면 검색 로직
        category = obj.category
        if not category:
            # 임시로 카테고리 추론 (아이콘을 위해)
             if obj.master_ingredient:
                 category = obj.master_ingredient.category
             elif master:
                 category = master.category
             else:
                 category = '기타'

        default_icons = {
            '채소': '🥬', '과일': '🍎', '육류': '🥩', '수산물': '🐟',
            '유제품': '🥛', '가공식품': '🥫', '음료': '🧃', '곡류': '🌾',
        }
        return default_icons.get(category, '📦')

    def create(self, validated_data):
        user = self.context['request'].user
        name = validated_data.get('name')
        expiry_date = validated_data.get('expiry_date')
        quantity = validated_data.get('quantity', 0)
        
        # 중복 체크
        existing = UserIngredient.objects.filter(
            user=user, 
            name=name, 
            expiry_date=expiry_date
        ).first()
        
        if existing:
            existing.quantity += quantity
            # 카테고리가 입력되었다면 업데이트
            if validated_data.get('category'):
                existing.category = validated_data.get('category')
            existing.save()
            return existing

        validated_data['user'] = user
        
        # 마스터 데이터 연결 및 카테고리 자동 채움
        from master.models import IngredientMaster
        master = None
        if name and 'master_ingredient' not in validated_data:
            master = IngredientMaster.objects.filter(name=name).first()
            if not master:
                master = IngredientMaster.objects.filter(name__iexact=name).first()
            if not master:
                master = IngredientMaster.objects.filter(name__icontains=name).first()
            
            if master:
                validated_data['master_ingredient'] = master
                # 카테고리가 입력되지 않았다면 마스터 데이터에서 가져옴
                if not validated_data.get('category'):
                    validated_data['category'] = master.category
                
        return super().create(validated_data)

class UserIngredientListSerializer(serializers.ModelSerializer):
    """식재료 목록 조회용 (간단한 정보만)"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    category = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    
    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'expiry_date',
            'is_expiring_soon', 'is_expired', 'category', 'icon', 'storage_method'
        ]
    
    def get_category(self, obj):
        """재료의 카테고리를 반환 (우선순위: 사용자 지정 > 마스터 > 자동추론)"""
        # 0. 사용자 지정
        if obj.category:
            return obj.category
            
        # 1. master_ingredient가 직접 연결되어 있는 경우
        if obj.master_ingredient:
            return obj.master_ingredient.category
        
        # 2. 이름으로 마스터 데이터 검색 (정확한 매칭)
        from master.models import IngredientMaster
        master = IngredientMaster.objects.filter(name=obj.name).first()
        if master:
            return master.category
        
        # 3. 대소문자 무시하고 검색
        master = IngredientMaster.objects.filter(name__iexact=obj.name).first()
        if master:
            return master.category
        
        # 4. 부분 매칭 시도
        master = IngredientMaster.objects.filter(name__icontains=obj.name).first()
        if master:
            return master.category
        
        # 5. 역방향 부분 매칭
        all_masters = IngredientMaster.objects.all()
        for m in all_masters:
            if m.name in obj.name or obj.name in m.name:
                return m.category
        
        return '기타'
    
    def get_icon(self, obj):
        """재료의 아이콘을 반환 (개선된 매칭)"""
        # 1. master_ingredient가 직접 연결되어 있는 경우
        if obj.master_ingredient and obj.master_ingredient.icon:
            return obj.master_ingredient.icon
        
        # 2. 이름으로 마스터 데이터 검색
        from master.models import IngredientMaster
        master = IngredientMaster.objects.filter(name=obj.name).first()
        if master and master.icon:
            return master.icon
        
        # 3. 대소문자 무시하고 검색
        master = IngredientMaster.objects.filter(name__iexact=obj.name).first()
        if master and master.icon:
            return master.icon
        
        # 4. 카테고리 기반 기본 아이콘
        category = self.get_category(obj)
        default_icons = {
            '채소': '🥬', '과일': '🍎', '육류': '🥩', '수산물': '🐟',
            '유제품': '🥛', '가공식품': '🥫', '음료': '🧃', '곡류': '🌾',
        }
        return default_icons.get(category, '📦')

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
