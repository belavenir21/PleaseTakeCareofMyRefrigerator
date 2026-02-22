"""
마스터 데이터 Views
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import IngredientMaster, IngredientSynonym, AllergyMaster
from .serializers import (
    IngredientMasterSerializer,
    IngredientMasterSimpleSerializer,
    AllergyMasterSerializer
)
from config.constants import INGREDIENT_CATEGORIES, CATEGORY_DEFAULTS


class IngredientMasterViewSet(viewsets.ReadOnlyModelViewSet):
    """식재료 마스터 ViewSet (읽기 전용)"""
    queryset = IngredientMaster.objects.all()
    serializer_class = IngredientMasterSerializer
    permission_classes = [AllowAny]  # 자동완성을 위해 공개
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'synonyms__synonym']  # 동의어도 검색 가능
    ordering_fields = ['name', 'category']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return IngredientMasterSimpleSerializer
        return IngredientMasterSerializer

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """카테고리 목록 반환"""
        categories = [
            {
                'name': cat[0],
                'defaults': CATEGORY_DEFAULTS.get(cat[0], {})
            }
            for cat in INGREDIENT_CATEGORIES
        ]
        return Response(categories)

    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """자동완성용 검색"""
        query = request.query_params.get('q', '')
        if len(query) < 1:
            return Response([])
        
        # 마스터에서 검색
        masters = IngredientMaster.objects.filter(name__icontains=query)[:10]
        
        # 동의어에서도 검색
        synonyms = IngredientSynonym.objects.filter(
            synonym__icontains=query
        ).select_related('master')[:5]
        
        results = []
        seen = set()
        
        # 마스터 결과 추가
        for m in masters:
            if m.name not in seen:
                results.append({
                    'id': m.id,
                    'name': m.name,
                    'category': m.category,
                    'icon': m.icon,
                    'unit': m.default_unit,
                    'storage_method': m.default_storage_method,
                    'expiry_days': m.default_expiry_days,
                })
                seen.add(m.name)
        
        # 동의어 결과 추가 (마스터로 변환)
        for s in synonyms:
            if s.master.name not in seen:
                results.append({
                    'id': s.master.id,
                    'name': s.master.name,
                    'category': s.master.category,
                    'icon': s.master.icon,
                    'unit': s.master.default_unit,
                    'storage_method': s.master.default_storage_method,
                    'expiry_days': s.master.default_expiry_days,
                    'matched_synonym': s.synonym  # 어떤 동의어로 매칭되었는지
                })
                seen.add(s.master.name)
        
        return Response(results[:15])


class AllergyMasterViewSet(viewsets.ReadOnlyModelViewSet):
    """알레르기 마스터 ViewSet (읽기 전용)"""
    queryset = AllergyMaster.objects.all()
    serializer_class = AllergyMasterSerializer
    permission_classes = [AllowAny]
