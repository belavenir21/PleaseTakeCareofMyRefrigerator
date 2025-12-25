from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """사용자 프로필 정보"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, blank=True, null=True)
    diet_goals = models.CharField(max_length=255, blank=True, null=True, help_text="식단 목표 (해시태그)")
    allergies = models.ManyToManyField('master.AllergyMaster', blank=True, related_name='profiles')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name='프로필 이미지')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        db_table = 'user_profiles'
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필'
