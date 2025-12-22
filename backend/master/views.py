from rest_framework import viewsets, permissions
from .models import IngredientMaster
from .serializers import IngredientMasterSerializer

class IngredientMasterViewSet(viewsets.ReadOnlyModelViewSet):
    """식재료 마스터 데이터 조회 (검색용)"""
    serializer_class = IngredientMasterSerializer
    permission_classes = [permissions.AllowAny]  # 누구나 검색 가능
    
    def get_queryset(self):
        # 검색어(search)가 있을 때만 결과를 반환
        search = self.request.query_params.get('search', None)
        if search and len(search) >= 1:
            # 동의어 처리
            synonyms = {
                '계란': '달걀', '특란': '달걀', '대란': '달걀', '왕란': '달걀',
                '쇠고기': '소고기',
                '무우': '무',
                '쪽파': '파', '대파': '파',
                '두유': '콩우유',
                '청양고추': '고추'
            }
            # 검색어가 동의어 키를 포함하면 값으로 치환 (단순 치환)
            for key, val in synonyms.items():
                if key in search:
                    search = search.replace(key, val)
                    
            return IngredientMaster.objects.filter(name__icontains=search)[:15]
        return IngredientMaster.objects.none()
