from rest_framework import serializers
from .models import UserIngredient

class UserIngredientSerializer(serializers.ModelSerializer):
    """사용자 식재료 Serializer"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    category = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    
    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'storage_method', 
            'expiry_date', 'image', 'created_at', 'updated_at',
            'is_expiring_soon', 'is_expired', 'category', 'icon'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_category(self, obj):
        """재료의 카테고리를 반환 (개선된 매칭)"""
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
        # 카테고리별 기본 아이콘
        default_icons = {
            '채소': '🥬', '과일': '🍎', '육류': '🥩', '수산물': '🐟',
            '유제품': '🥛', '가공식품': '🥫', '음료': '🧃', '곡류': '🌾',
        }
        return default_icons.get(category, '📦')

    def create(self, validated_data):
        # 사용자 정보 자동 설정
        user = self.context['request'].user
        name = validated_data.get('name')
        expiry_date = validated_data.get('expiry_date')
        quantity = validated_data.get('quantity', 0)
        
        # 중복 체크 (유저, 이름, 유통기한이 같은 경우)
        existing = UserIngredient.objects.filter(
            user=user, 
            name=name, 
            expiry_date=expiry_date
        ).first()
        
        if existing:
            # 기존 항목이 있으면 수량을 합산
            existing.quantity += quantity
            # 보관 방법이나 단위는 새로 들어온 데이터로 갱신할 수도 있지만 
            # 일단 수량만 합치는 방향으로 진행
            existing.save()
            return existing

        # 새 항목 생성 시 사용자 정보 할당
        validated_data['user'] = user
        
        # 마스터 데이터 자동 연결 시도 (개선된 매칭)
        from master.models import IngredientMaster
        if name and 'master_ingredient' not in validated_data:
            # 1. 정확한 매칭
            master = IngredientMaster.objects.filter(name=name).first()
            if not master:
                # 2. 대소문자 무시
                master = IngredientMaster.objects.filter(name__iexact=name).first()
            if not master:
                # 3. 부분 매칭
                master = IngredientMaster.objects.filter(name__icontains=name).first()
            if master:
                validated_data['master_ingredient'] = master
                
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
        """재료의 카테고리를 반환 (개선된 매칭)"""
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
        
        # 4. 부분 매칭 시도 (재료 이름이 마스터 이름에 포함되거나 그 반대)
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
