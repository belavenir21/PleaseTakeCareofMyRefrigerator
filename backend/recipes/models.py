from django.db import models

class Recipe(models.Model):
    """레시피"""
    title = models.CharField(max_length=200, verbose_name='레시피명')
    description = models.TextField(verbose_name='설명')
    cooking_time_minutes = models.IntegerField(verbose_name='조리시간(분)')
    difficulty = models.CharField(max_length=20, verbose_name='난이도')
    image_url = models.URLField(blank=True, null=True, verbose_name='이미지 URL')
    tags = models.JSONField(default=list, blank=True, verbose_name='태그')
    
    # 외부 API 데이터
    api_source = models.CharField(max_length=50, blank=True, null=True, verbose_name='데이터 출처')
    api_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='외부 API ID')
    
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
    """레시피 재료"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100, verbose_name='재료명')
    quantity = models.CharField(max_length=50, verbose_name='수량')
    
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
