"""
사용자 냉장고/보관함 모델
"""
from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


class UserIngredient(models.Model):
    """사용자가 보관 중인 식재료"""
    STORAGE_CHOICES = [
        ('냉장', '냉장'),
        ('냉동', '냉동'),
        ('실온', '실온'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    
    # 마스터 데이터 연결 (주요 개선: 마스터 연결 권장)
    master = models.ForeignKey(
        'master.IngredientMaster',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_ingredients',
        verbose_name='마스터 식재료'
    )
    
    # name은 마스터 없을 때 폴백용 또는 표시용
    name = models.CharField(max_length=100, verbose_name='재료명')
    quantity = models.FloatField(default=1, verbose_name='수량')
    unit = models.CharField(max_length=20, default='개', verbose_name='단위')
    storage_method = models.CharField(
        max_length=20,
        choices=STORAGE_CHOICES,
        default='냉장',
        verbose_name='보관방법'
    )
    expiry_date = models.DateField(verbose_name='유통기한')
    
    # Soft Delete
    is_deleted = models.BooleanField(default=False, verbose_name='삭제여부')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='삭제일시')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'user_ingredients'
        verbose_name = '사용자 식재료'
        verbose_name_plural = '사용자 식재료'
        ordering = ['expiry_date', 'name']
        indexes = [
            models.Index(fields=['user', 'expiry_date']),
            models.Index(fields=['user', 'is_deleted']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.quantity}{self.unit})"

    @property
    def is_expiring_soon(self) -> bool:
        """유통기한이 3일 이내인지 확인"""
        if not self.expiry_date:
            return False
        exp_date = self.expiry_date
        if isinstance(exp_date, str):
            from datetime import datetime
            exp_date = datetime.strptime(exp_date, '%Y-%m-%d').date()
        return exp_date <= date.today() + timedelta(days=3)

    @property
    def is_expired(self) -> bool:
        """유통기한이 지났는지 확인"""
        if not self.expiry_date:
            return False
        exp_date = self.expiry_date
        if isinstance(exp_date, str):
            from datetime import datetime
            exp_date = datetime.strptime(exp_date, '%Y-%m-%d').date()
        return exp_date < date.today()
    
    @property
    def category(self) -> str:
        """카테고리 반환 (마스터에서 가져옴)"""
        if self.master:
            return self.master.category
        return '기타'
    
    @property
    def icon(self) -> str:
        """아이콘 반환 (마스터에서 가져옴)"""
        if self.master and self.master.icon:
            return self.master.icon
        return '📦'
    
    @property
    def image_url(self) -> str:
        """이미지 URL 반환 (마스터에서 가져옴)"""
        if self.master and self.master.image_url:
            return self.master.image_url
        return None

    def save(self, *args, **kwargs):
        # 마스터 자동 연결 시도
        if not self.master and self.name:
            from master.models import find_master_by_name
            self.master = find_master_by_name(self.name)
            
            # 마스터가 연결되면 마스터 이름으로 정규화
            if self.master:
                self.name = self.master.name
        
        super().save(*args, **kwargs)
