"""
마스터 데이터 모델 - V2
식재료 마스터, 동의어, 알레르기 정보 관리
"""
from django.db import models
from config.constants import (
    INGREDIENT_CATEGORIES,
    STORAGE_METHODS,
    CATEGORY_DEFAULTS,
)


class IngredientMaster(models.Model):
    """식재료 마스터 데이터"""
    name = models.CharField(max_length=100, unique=True, verbose_name='재료명')
    category = models.CharField(
        max_length=50,
        choices=INGREDIENT_CATEGORIES,
        default='기타',
        verbose_name='카테고리'
    )
    default_unit = models.CharField(max_length=20, default='개', verbose_name='기본 단위')
    default_storage_method = models.CharField(
        max_length=20,
        choices=STORAGE_METHODS,
        default='냉장',
        verbose_name='기본 보관방법'
    )
    default_expiry_days = models.IntegerField(default=14, verbose_name='기본 유통기한(일)')
    icon = models.CharField(max_length=10, blank=True, default='📦', verbose_name='이모지 아이콘')
    image_url = models.URLField(blank=True, null=True, verbose_name='커스텀 아이콘 URL')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ingredient_master'
        verbose_name = '식재료 마스터'
        verbose_name_plural = '식재료 마스터'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # 카테고리 기반 기본값 자동 설정 (값이 없을 때만)
        if self.category in CATEGORY_DEFAULTS:
            defaults = CATEGORY_DEFAULTS[self.category]
            if not self.default_storage_method:
                self.default_storage_method = defaults['storage']
            if self.default_expiry_days == 14:  # 기본값일 때만
                self.default_expiry_days = defaults['days']
            if not self.icon or self.icon == '📦':
                self.icon = defaults['icon']
        super().save(*args, **kwargs)


class IngredientSynonym(models.Model):
    """식재료 동의어 - 검색 및 매칭 시 활용"""
    master = models.ForeignKey(
        IngredientMaster,
        on_delete=models.CASCADE,
        related_name='synonyms',
        verbose_name='마스터 식재료'
    )
    synonym = models.CharField(max_length=100, unique=True, verbose_name='동의어')

    class Meta:
        db_table = 'ingredient_synonym'
        verbose_name = '식재료 동의어'
        verbose_name_plural = '식재료 동의어'

    def __str__(self):
        return f"{self.synonym} → {self.master.name}"


class AllergyMaster(models.Model):
    """알레르기 마스터 데이터"""
    name = models.CharField(max_length=50, unique=True, verbose_name='알레르기명')
    description = models.TextField(blank=True, null=True, verbose_name='설명')

    class Meta:
        db_table = 'allergy_master'
        verbose_name = '알레르기 마스터'
        verbose_name_plural = '알레르기 마스터'
        ordering = ['name']

    def __str__(self):
        return self.name


# ===== 유틸리티 함수 =====

def find_master_by_name(name: str):
    """
    이름으로 마스터 식재료 찾기 (동의어 포함)
    
    Args:
        name: 검색할 식재료명
        
    Returns:
        IngredientMaster 또는 None
    """
    if not name:
        return None
    
    name = name.strip()
    
    # 1. 정확히 일치
    master = IngredientMaster.objects.filter(name=name).first()
    if master:
        return master
    
    # 2. 동의어에서 검색
    synonym = IngredientSynonym.objects.filter(synonym=name).first()
    if synonym:
        return synonym.master
    
    # 3. 대소문자 무시 검색
    master = IngredientMaster.objects.filter(name__iexact=name).first()
    if master:
        return master
    
    # 4. 동의어 대소문자 무시
    synonym = IngredientSynonym.objects.filter(synonym__iexact=name).first()
    if synonym:
        return synonym.master
    
    # 5. 포함 검색 (마스터 이름이 검색어에 포함)
    for m in IngredientMaster.objects.all():
        if m.name in name:
            return m
    
    return None
