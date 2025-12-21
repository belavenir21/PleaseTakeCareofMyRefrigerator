from django.db import models

class IngredientMaster(models.Model):
    """식재료 마스터 데이터"""
    name = models.CharField(max_length=100, unique=True, verbose_name='재료명')
    category = models.CharField(max_length=50, verbose_name='카테고리')
    default_unit = models.CharField(max_length=10, verbose_name='기본 단위')
    icon = models.CharField(max_length=10, blank=True, null=True, verbose_name='이모지 아이콘')
    image_url = models.URLField(blank=True, null=True, verbose_name='이미지 URL')
    
    # 외부 API 데이터
    api_source = models.CharField(max_length=50, blank=True, null=True, verbose_name='데이터 출처')
    api_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='외부 API ID')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 알레르기 유발 성분 연결
    allergies = models.ManyToManyField('AllergyMaster', blank=True, related_name='ingredients')
    
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
