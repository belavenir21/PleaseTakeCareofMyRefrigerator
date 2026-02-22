"""
사용자 식재료 Serializers - V2
마스터 연결 강화, category/icon은 마스터에서 자동 가져옴
"""
from rest_framework import serializers
from .models import UserIngredient
from master.models import IngredientMaster, find_master_by_name
from config.constants import CATEGORY_DEFAULTS


class UserIngredientSerializer(serializers.ModelSerializer):
    """사용자 식재료 Serializer (상세)"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    category = serializers.ReadOnlyField()  # property에서 가져옴
    icon = serializers.ReadOnlyField()      # property에서 가져옴
    image_url = serializers.ReadOnlyField() # property에서 가져옴
    master_id = serializers.PrimaryKeyRelatedField(
        source='master',
        queryset=IngredientMaster.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'storage_method',
            'expiry_date', 'created_at', 'updated_at',
            'is_expiring_soon', 'is_expired',
            'category', 'icon', 'image_url', 'master_id'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        name = validated_data.get('name', '').strip()
        expiry_date = validated_data.get('expiry_date')
        quantity = validated_data.get('quantity', 1)

        # 마스터 자동 연결
        master = validated_data.get('master')
        if not master and name:
            master = find_master_by_name(name)
            if master:
                validated_data['master'] = master
                validated_data['name'] = master.name  # 정규화된 이름 사용

        # 중복 체크 (같은 이름 + 같은 유통기한)
        existing = UserIngredient.objects.filter(
            user=user,
            name=validated_data.get('name', name),
            expiry_date=expiry_date,
            is_deleted=False
        ).first()

        if existing:
            existing.quantity += quantity
            existing.save()
            return existing

        validated_data['user'] = user
        return super().create(validated_data)


class UserIngredientListSerializer(serializers.ModelSerializer):
    """식재료 목록 조회용 (간단한 정보)"""
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    category = serializers.ReadOnlyField()
    icon = serializers.ReadOnlyField()
    image_url = serializers.ReadOnlyField()

    class Meta:
        model = UserIngredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'storage_method', 'expiry_date',
            'is_expiring_soon', 'is_expired', 'category', 'icon', 'image_url'
        ]


class IngredientScanSerializer(serializers.Serializer):
    """사진 스캔용 Serializer"""
    image = serializers.ImageField()


class IngredientBatchCreateSerializer(serializers.Serializer):
    """여러 식재료 일괄 등록"""
    ingredients = serializers.ListField(
        child=serializers.DictField()
    )

    def create(self, validated_data):
        user = self.context['request'].user
        ingredients_data = validated_data['ingredients']
        created = []
        updated = []
        errors = []

        for item in ingredients_data:
            try:
                name = item.get('name', '').strip()
                if not name:
                    continue

                # 마스터 찾기
                master = find_master_by_name(name)
                if master:
                    name = master.name

                # 기본값 설정
                category = item.get('category', '기타')
                defaults = CATEGORY_DEFAULTS.get(category, CATEGORY_DEFAULTS['기타'])
                expiry_date = item.get('expiry_date')
                quantity = float(item.get('quantity', 1))

                # 중복 체크 (같은 이름 + 같은 유통기한)
                existing = UserIngredient.objects.filter(
                    user=user,
                    name=name,
                    expiry_date=expiry_date,
                    is_deleted=False
                ).first()

                if existing:
                    # 기존 항목에 수량 추가
                    existing.quantity += quantity
                    existing.save()
                    updated.append(existing)
                else:
                    # 새로 생성
                    ingredient = UserIngredient.objects.create(
                        user=user,
                        master=master,
                        name=name,
                        quantity=quantity,
                        unit=item.get('unit', master.default_unit if master else '개'),
                        storage_method=item.get('storage_method', defaults['storage']),
                        expiry_date=expiry_date,
                    )
                    created.append(ingredient)
            except Exception as e:
                errors.append({'item': item, 'error': str(e)})

        return {'created': created, 'updated': updated, 'errors': errors}
