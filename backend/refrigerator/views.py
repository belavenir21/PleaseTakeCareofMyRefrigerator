"""
사용자 식재료 관리 Views - V2
마스터 연결 강화, 중복 코드 제거, AI 로직 분리
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters import rest_framework as filters
from datetime import date, timedelta, datetime
from django.conf import settings
from django.utils import timezone

from .models import UserIngredient
from .serializers import (
    UserIngredientSerializer,
    UserIngredientListSerializer,
    IngredientScanSerializer,
    IngredientBatchCreateSerializer
)
from master.models import IngredientMaster, find_master_by_name
from config.constants import CATEGORY_DEFAULTS
from config.authentication import CsrfExemptSessionAuthentication


class UserIngredientFilter(filters.FilterSet):
    """식재료 필터"""
    storage_method = filters.CharFilter(field_name='storage_method')
    expiring_soon = filters.BooleanFilter(method='filter_expiring_soon')
    expired = filters.BooleanFilter(method='filter_expired')

    class Meta:
        model = UserIngredient
        fields = ['storage_method']

    def filter_expiring_soon(self, queryset, name, value):
        if value:
            soon_date = date.today() + timedelta(days=3)
            return queryset.filter(expiry_date__lte=soon_date, expiry_date__gte=date.today())
        return queryset

    def filter_expired(self, queryset, name, value):
        if value:
            return queryset.filter(expiry_date__lt=date.today())
        return queryset


class UserIngredientViewSet(viewsets.ModelViewSet):
    """사용자 식재료 관리 ViewSet"""
    serializer_class = UserIngredientSerializer
    filterset_class = UserIngredientFilter
    search_fields = ['name']
    ordering_fields = ['expiry_date', 'name', 'created_at']
    ordering = ['expiry_date']
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserIngredient.objects.filter(user=self.request.user, is_deleted=False)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserIngredientListSerializer
        return UserIngredientSerializer

    # ===== CRUD Override =====

    def destroy(self, request, *args, **kwargs):
        """Soft Delete"""
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ===== 휴지통 관련 =====

    @action(detail=False, methods=['get'])
    def trash(self, request):
        """휴지통 목록 조회"""
        queryset = UserIngredient.objects.filter(
            user=request.user, is_deleted=True
        ).order_by('-deleted_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """휴지통 항목 복구"""
        try:
            instance = UserIngredient.objects.get(pk=pk, user=request.user, is_deleted=True)
            instance.is_deleted = False
            instance.deleted_at = None
            instance.save()
            return Response({
                'status': 'restored',
                'message': f'{instance.name} 복구되었습니다.'
            })
        except UserIngredient.DoesNotExist:
            return Response({'error': '항목을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'])
    def hard_delete(self, request, pk=None):
        """영구 삭제"""
        try:
            instance = UserIngredient.objects.get(pk=pk, user=request.user)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserIngredient.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def empty_trash(self, request):
        """휴지통 비우기"""
        trash_items = UserIngredient.objects.filter(user=request.user, is_deleted=True)
        count = trash_items.count()
        trash_items.delete()
        return Response({'message': f'{count}개의 항목이 영구 삭제되었습니다.'})

    # ===== 알림 및 일괄 작업 =====

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """유통기한 임박 식재료 조회"""
        soon_date = date.today() + timedelta(days=3)
        expiring = self.get_queryset().filter(
            expiry_date__lte=soon_date,
            expiry_date__gte=date.today()
        )
        serializer = UserIngredientListSerializer(expiring, many=True)
        return Response({
            'count': expiring.count(),
            'ingredients': serializer.data
        })

    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """여러 식재료 일괄 추가"""
        serializer = IngredientBatchCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            result = serializer.save()
            created_serializer = UserIngredientListSerializer(result['created'], many=True)
            updated_serializer = UserIngredientListSerializer(result.get('updated', []), many=True)
            return Response({
                'created': created_serializer.data,
                'updated': updated_serializer.data,
                'created_count': len(result['created']),
                'updated_count': len(result.get('updated', [])),
                'errors': result['errors']
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """여러 식재료 일괄 삭제"""
        ids = request.data.get('ids', [])
        UserIngredient.objects.filter(
            id__in=ids, user=request.user
        ).update(is_deleted=True, deleted_at=timezone.now())
        return Response({'message': f'{len(ids)}개 항목이 삭제되었습니다.'})

    @action(detail=False, methods=['post'])
    def clear_expired(self, request):
        """유통기한 지난 재료 일괄 삭제"""
        expired = self.get_queryset().filter(expiry_date__lt=date.today())
        count = expired.count()
        expired.update(is_deleted=True, deleted_at=timezone.now())
        return Response({'message': f'{count}개의 만료된 항목이 삭제되었습니다.'})

    # ===== 재료 소진/버리기 =====

    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """재료 소진 (수량 차감)"""
        instance = self.get_object()
        quantity = float(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response({'error': '차감 수량이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity >= instance.quantity:
            # 완전 소진 → 삭제
            instance.is_deleted = True
            instance.deleted_at = timezone.now()
            instance.save()
            return Response({'deleted': True, 'remaining_quantity': 0})
        else:
            instance.quantity -= quantity
            instance.save()
            return Response({'deleted': False, 'remaining_quantity': instance.quantity})

    @action(detail=True, methods=['post'])
    def discard(self, request, pk=None):
        """재료 부분 버리기 (휴지통으로)"""
        instance = self.get_object()
        quantity = float(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response({'error': '버릴 수량이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity >= instance.quantity:
            # 전체 버리기
            instance.is_deleted = True
            instance.deleted_at = timezone.now()
            instance.save()
            return Response({'discarded': True, 'remaining_quantity': 0})
        else:
            # 일부만 버리기 - 버린 부분은 별도 휴지통 항목으로 생성
            discarded_item = UserIngredient.objects.create(
                user=instance.user,
                master=instance.master,
                name=instance.name,
                quantity=quantity,
                unit=instance.unit,
                storage_method=instance.storage_method,
                expiry_date=instance.expiry_date,
                is_deleted=True,
                deleted_at=timezone.now()
            )
            instance.quantity -= quantity
            instance.save()
            return Response({
                'discarded': False,
                'remaining_quantity': instance.quantity,
                'discarded_quantity': quantity
            })

    # ===== AI 식재료 인식 =====

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def scan(self, request):
        """영수증 스캔 (AI 분석)"""
        from .ai_services import analyze_receipt
        
        serializer = IngredientScanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        image = serializer.validated_data['image']
        
        try:
            result = analyze_receipt(image)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            error_msg = str(e)
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "API 키" in error_msg or "한도" in error_msg or "토큰" in error_msg else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({'error': error_msg}, status=status_code)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def identify_ingredients_ai(self, request):
        """사진으로 식재료 인식 (AI Vision)"""
        from .ai_services import identify_ingredients_from_image
        
        serializer = IngredientScanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        image = serializer.validated_data['image']
        
        try:
            result = identify_ingredients_from_image(image)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            error_msg = str(e)
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "API 키" in error_msg or "한도" in error_msg or "토큰" in error_msg else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({'error': error_msg}, status=status_code)
