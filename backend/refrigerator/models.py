from django.db import models
from django.contrib.auth.models import User
from master.models import IngredientMaster

class UserIngredient(models.Model):
    """사용자가 보관 중인 식재료"""
    STORAGE_CHOICES = [
        ('냉장', '냉장'),
        ('냉동', '냉동'),
        ('실온', '실온'),
    ]
    
    UNIT_CHOICES = [
        ('g', '그램'),
        ('ml', '밀리리터'),
        ('개', '개'),
        ('봉', '봉'),
        ('팩', '팩'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100, verbose_name='재료명')
    quantity = models.FloatField(verbose_name='수량')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='g', verbose_name='단위')
    storage_method = models.CharField(max_length=10, choices=STORAGE_CHOICES, verbose_name='보관방법')
    expiry_date = models.DateField(verbose_name='유통기한')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    # 마스터 데이터 연결 (옵션)
    master_ingredient = models.ForeignKey(
        IngredientMaster, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_ingredients'
    )
    
    # 이미지 (사진 촬영 시 저장)
    image = models.ImageField(upload_to='ingredients/', null=True, blank=True)
    
    class Meta:
        db_table = 'user_ingredients'
        verbose_name = '사용자 식재료'
        verbose_name_plural = '사용자 식재료'
        ordering = ['expiry_date', 'name']
        indexes = [
            models.Index(fields=['user', 'expiry_date']),
            models.Index(fields=['user', 'name']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.quantity}{self.unit})"
    
    @property
    def is_expiring_soon(self):
        """유통기한이 3일 이내인지 확인"""
        from datetime import date, timedelta
        return self.expiry_date <= date.today() + timedelta(days=3)
    
    @property
    def is_expired(self):
        """유통기한이 지났는지 확인"""
        from datetime import date
        return self.expiry_date < date.today()
