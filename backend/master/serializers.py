from rest_framework import serializers
from .models import IngredientMaster

class IngredientMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientMaster
        fields = ['id', 'name', 'category', 'default_unit', 'icon', 'image_url']
