"""
마스터 데이터 Serializers
"""
from rest_framework import serializers
from .models import IngredientMaster, IngredientSynonym, AllergyMaster


class IngredientSynonymSerializer(serializers.ModelSerializer):
    """동의어 Serializer"""
    class Meta:
        model = IngredientSynonym
        fields = ['id', 'synonym']


class IngredientMasterSerializer(serializers.ModelSerializer):
    """식재료 마스터 Serializer"""
    synonyms = IngredientSynonymSerializer(many=True, read_only=True)
    
    class Meta:
        model = IngredientMaster
        fields = [
            'id', 'name', 'category', 'default_unit',
            'default_storage_method', 'default_expiry_days',
            'icon', 'image_url', 'synonyms'
        ]


class IngredientMasterSimpleSerializer(serializers.ModelSerializer):
    """식재료 마스터 간단 Serializer (자동완성용)"""
    class Meta:
        model = IngredientMaster
        fields = ['id', 'name', 'category', 'default_unit', 'icon', 'image_url']


class AllergyMasterSerializer(serializers.ModelSerializer):
    """알레르기 마스터 Serializer"""
    class Meta:
        model = AllergyMaster
        fields = ['id', 'name', 'description']
