from rest_framework import viewsets
from .models import IngredientMaster
from .serializers import IngredientMasterSerializer

class IngredientMasterViewSet(viewsets.ReadOnlyModelViewSet):
    """식재료 마스터 데이터 조회 (검색용)"""
    serializer_class = IngredientMasterSerializer
    
    def get_queryset(self):
        # 검색어(search)가 있을 때만 결과를 반환 (성능 및 UX 고려)
        search = self.request.query_params.get('search', None)
        if search and len(search) >= 1: # 1글자 이상일 때만
            return IngredientMaster.objects.filter(name__icontains=search)[:10]
        return IngredientMaster.objects.none()
