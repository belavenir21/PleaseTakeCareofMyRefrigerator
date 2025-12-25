from rest_framework import serializers
from .models import UserIngredient

class UserIngredientSerializer(serializers.ModelSerializer):
    """사용자 식재료 Serializer"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    # category는 모델 필드를 그대로 사용 (쓰기 가능)
    icon = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'storage_method', 
            'expiry_date', 'image', 'created_at', 'updated_at',
            'is_expiring_soon', 'is_expired', 'category', 'icon', 'image_url'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'category': {'required': False, 'allow_null': True, 'allow_blank': True}
        }

    def validate_name(self, value):
        """마스터 DB에 있는 재료인지 검증"""
        from master.models import IngredientMaster
        name = value.strip()
        
        # 동의어 매핑 (검증용)
        synonyms = {
            "계란": "달걀", "삼겹살": "돼지고기", "스팸": "햄", "참치캔": "참치",
            "무": "달랑무", "애호박": "호박", "방울토마토": "토마토", "공기밥": "국밥",
            "파": "대파", "마늘": "다진마늘"
        }
        
        if name in synonyms:
            name = synonyms[name]

        # 1. 완전 일치
        if IngredientMaster.objects.filter(name=name).exists():
            return name
        
        # 2. 대소문자 무시
        master = IngredientMaster.objects.filter(name__iexact=name).first()
        if master:
            return master.name
            
        # 3. 포함 관계 (주방 -> 주방용품 차단 등을 위해 신중히)
        # 하지만 사용자가 "국산 양파"라고 입력했을 때 "양파"로 매칭해주면 좋음
        masters = IngredientMaster.objects.all()
        for m in masters:
            if m.name in name: # "양파" in "국산양파"
                return m.name
            if name in m.name: # "양파" in "빨간양파" (일부 가능)
                return m.name

        return value.strip()
    
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
            '채소': '🥬',
            '과일/견과': '🍎',
            '수산/건어물': '🐟',
            '육류/달걀': '🥩',
            '유제품': '🥛',
            '곡류': '🌾',
            '면/양념/오일': '🍜',
            '가공식품': '🥫',
            '간편식/식단': '🍱',
            '음료': '🧃',
            '기타': '📦'
        }
        return default_icons.get(category, '📦')

    def get_image_url(self, obj):
        """마스터 데이터의 이미지 URL(아이콘) 반환"""
        if obj.master_ingredient and obj.master_ingredient.image_url:
            return obj.master_ingredient.image_url
        
        # 이름으로 다시 검색 (연결 안 된 경우 대비)
        from master.models import IngredientMaster
        
        # 동의어 매핑
        synonyms = {
            "계란": "달걀", "삼겹살": "돼지고기", "스팸": "햄", "참치캔": "참치",
            "무": "달랑무", "애호박": "호박", "방울토마토": "토마토", "파": "대파",
            "마늘": "다진마늘", "공기밥": "국밥"
        }
        
        search_name = obj.name
        if search_name in synonyms:
            search_name = synonyms[search_name]
            
        master = IngredientMaster.objects.filter(name=search_name).first()
        if not master:
            master = IngredientMaster.objects.filter(name__iexact=search_name).first()
        if not master:
            # 부분 일치 검색 (이미지 URL을 찾기 위함)
            master = IngredientMaster.objects.filter(name__icontains=search_name).first()
            
        if master and master.image_url:
            return master.image_url
        return None

    def create(self, validated_data):
        user = self.context['request'].user
        name = validated_data.get('name')
        expiry_date = validated_data.get('expiry_date')
        quantity = validated_data.get('quantity', 0)
        
        # 중복 체크: 현재 활성 상태인(is_deleted=False) 항목만 검색
        existing = UserIngredient.objects.filter(
            user=user, 
            name=name, 
            expiry_date=expiry_date,
            is_deleted=False
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
            else:
                # [NEW] Master에 없는 재료는 자동 생성!
                try:
                    category = validated_data.get('category', '기타') or '기타'
                    unit = validated_data.get('unit', '개')
                    
                    # 아이콘 자동 매핑
                    icon_map = {
                        '채소': '🥬', '과일/견과': '🍎', '수산/건어물': '🐟',
                        '육류/달걀': '🥩', '유제품': '🥛', '곡류': '🌾',
                        '면/양념/오일': '🍜', '가공식품': '🥫', '간편식/식단': '🍱',
                        '음료': '🧃', '기타': '📦'
                    }
                    icon = icon_map.get(category, '📦')

                    new_master = IngredientMaster.objects.create(
                        name=name,
                        category=category,
                        default_unit=unit,
                        icon=icon,
                        api_source='User_Manual_Auto'
                    )
                    validated_data['master_ingredient'] = new_master
                    if not validated_data.get('category'):
                        validated_data['category'] = category
                except Exception as e:
                    print(f"Error auto-creating master: {e}")
                
        return super().create(validated_data)

class UserIngredientListSerializer(serializers.ModelSerializer):
    """식재료 목록 조회용 (간단한 정보만)"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    category = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'expiry_date',
            'is_expiring_soon', 'is_expired', 'category', 'icon', 'storage_method', 'image_url'
        ]
    
    def get_category(self, obj):
        """재료의 카테고리를 반환 (우선순위: 사용자 지정 > 마스터 > 자동추론)"""
        from config.constants import normalize_category
        cat = '기타'
        
        # 0. 사용자 지정
        if obj.category:
            cat = obj.category
        # 1. master_ingredient가 직접 연결되어 있는 경우
        elif obj.master_ingredient:
            cat = obj.master_ingredient.category
        else:
            # 2. 이름으로 마스터 데이터 검색
            from master.models import IngredientMaster
            master = IngredientMaster.objects.filter(name=obj.name).first()
            if not master:
                master = IngredientMaster.objects.filter(name__iexact=obj.name).first()
            if not master:
                master = IngredientMaster.objects.filter(name__icontains=obj.name).first()
            
            if master:
                cat = master.category
            else:
                # 3. 역방향 부분 매칭
                all_masters = IngredientMaster.objects.all()
                for m in all_masters:
                    if m.name in obj.name or obj.name in m.name:
                        cat = m.category
                        break
        
        return normalize_category(cat)
    
    def get_icon(self, obj):
        """재료의 아이콘을 반환 (개선된 매칭)"""
        generic_icons = ['🥘', '🍴', '📦', '🛒', '🍽️', '', None]
        
        # 1. master_ingredient 확인
        if obj.master_ingredient and obj.master_ingredient.icon not in generic_icons:
            return obj.master_ingredient.icon
        
        # 2. 이름으로 마스터 데이터 검색
        from master.models import IngredientMaster
        master = IngredientMaster.objects.filter(name=obj.name).first()
        if master and master.icon not in generic_icons:
            return master.icon
            
        # 4. 카테고리 기반 기본 아이콘 (최종 폴백)
        category = self.get_category(obj)
        default_icons = {
            '채소': '🥬',
            '과일/견과': '🍎',
            '수산물': '🐟',
            '육류/달걀': '🥩',
            '유제품': '🥛',
            '곡류': '🌾',
            '양념/오일': '🧂',
            '가공식품': '🥫',
            '간편식': '🍱',
            '음료': '🧃',
            '기타': '📦'
        }
        return default_icons.get(category, '📦')

    def get_image_url(self, obj):
        """마스터 데이터의 이미지 URL(아이콘) 반환"""
        if obj.master_ingredient and obj.master_ingredient.image_url:
            return obj.master_ingredient.image_url
        
        from master.models import IngredientMaster
        
        # 동의어 매핑
        synonyms = {
            "계란": "달걀", "삼겹살": "돼지고기", "스팸": "햄", "참치캔": "참치",
            "무": "달랑무", "애호박": "호박", "방울토마토": "토마토"
        }
        
        search_name = obj.name
        if search_name in synonyms:
            search_name = synonyms[search_name]
            
        master = IngredientMaster.objects.filter(name=search_name).first()
        if not master:
            master = IngredientMaster.objects.filter(name__icontains=search_name).first()
            
        if master and master.image_url:
            return master.image_url
        return None

class IngredientScanSerializer(serializers.Serializer):
    """사진 스캔을 통한 식재료 등록"""
    image = serializers.ImageField()
    
class IngredientBulkCreateSerializer(serializers.Serializer):
    """여러 식재료 일괄 등록"""
    ingredients = UserIngredientSerializer(many=True)
    
    def create(self, validated_data):
        ingredients_data = validated_data['ingredients']
        user = self.context['request'].user
        
        from master.models import IngredientMaster

        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_data['user'] = user
            
            # Master 연결 및 자동 생성 로직 (UserIngredientSerializer.create와 동일하게 적용)
            name = ingredient_data.get('name')
            if name:
                master = IngredientMaster.objects.filter(name=name).first()
                if not master:
                     master = IngredientMaster.objects.filter(name__iexact=name).first()
                
                if not master:
                    # Auto Create Master
                    try:
                        category = ingredient_data.get('category', '기타') or '기타'
                        unit = ingredient_data.get('unit', '개')
                         # 아이콘 자동 매핑
                        icon_map = {
                            '채소': '🥬', '과일/견과': '🍎', '수산/건어물': '🐟',
                            '육류/달걀': '🥩', '유제품': '🥛', '곡류': '🌾',
                            '면/양념/오일': '🍜', '가공식품': '🥫', '간편식/식단': '🍱',
                            '음료': '🧃', '기타': '📦'
                        }
                        icon = icon_map.get(category, '📦')
                        
                        master = IngredientMaster.objects.create(
                            name=name,
                            category=category,
                            default_unit=unit,
                            icon=icon,
                            api_source='User_Bulk_Auto'
                        )
                    except Exception as e:
                        print(f"Bulk Create Master Error: {e}")
                
                if master:
                    ingredient_data['master_ingredient'] = master
                    if not ingredient_data.get('category'):
                         ingredient_data['category'] = master.category

            ingredient = UserIngredient.objects.create(**ingredient_data)
            ingredients.append(ingredient)
        
        return {'ingredients': ingredients}
