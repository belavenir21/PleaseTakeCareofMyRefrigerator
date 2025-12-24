from django.db import models
from django.conf import settings

class Recipe(models.Model):
    """레시피"""
    title = models.CharField(max_length=200, verbose_name='레시피명')
    description = models.TextField(verbose_name='설명')
    cooking_time_minutes = models.IntegerField(verbose_name='조리시간(분)')
    difficulty = models.CharField(max_length=20, verbose_name='난이도')
    image_url = models.URLField(blank=True, null=True, verbose_name='이미지 URL')
    image = models.ImageField(upload_to='recipe_images/', blank=True, null=True, verbose_name='업로드 이미지')  # Pillow 필요
    tags = models.JSONField(default=list, blank=True, verbose_name='태그')
    category = models.CharField(max_length=50, default='기타', verbose_name='카테고리')
    
    # 외부 API 데이터
    api_source = models.CharField(max_length=50, blank=True, null=True, verbose_name='데이터 출처')
    api_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='외부 API ID')
    
    # 작성자 (유저 레시피인 경우)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='recipes',
        verbose_name='작성자'
    )
    
    # 스크랩(즐겨찾기)한 유저들
    scraped_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='scraped_recipes',
        blank=True,
        verbose_name='스크랩한 유저'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recipes'
        verbose_name = '레시피'
        verbose_name_plural = '레시피'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    """레시피 재료 (수량 필드 제거: 93.9%가 '적정량'으로 의미 없음)"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100, verbose_name='재료명')
    # quantity 필드 제거됨 (2025.12.24)
    # 이유: 10,137개 중 9,519개(93.9%)가 "적정량"으로 실질적 정보 제공 불가
    
    class Meta:
        db_table = 'recipe_ingredients'
        verbose_name = '레시피 재료'
        verbose_name_plural = '레시피 재료'
    
    def __str__(self):
        return f"{self.recipe.title} - {self.name}"

class CookingStep(models.Model):
    """조리 단계"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField(verbose_name='단계 번호')
    description = models.TextField(verbose_name='설명')
    icon = models.CharField(max_length=10, blank=True, null=True, verbose_name='아이콘')
    time_minutes = models.IntegerField(default=0, verbose_name='소요시간(분)')
    
    class Meta:
        db_table = 'cooking_steps'
        verbose_name = '조리 단계'
        verbose_name_plural = '조리 단계'
        ordering = ['recipe', 'step_number']
    
    def __str__(self):
        return f"{self.recipe.title} - Step {self.step_number}"
