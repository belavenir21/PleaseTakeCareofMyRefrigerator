
import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def fix_nicknames():
    print("Starting nickname fix process...")
    
    # 1. 프로필이 없는 유저에게 프로필 생성 + 닉네임 설정
    users_without_profile = []
    for user in User.objects.all():
        if not hasattr(user, 'profile'):
            print(f"Creating profile for user: {user.username}")
            UserProfile.objects.create(user=user, nickname=user.username)
            users_without_profile.append(user.username)
            
    print(f"Created {len(users_without_profile)} missing profiles.")

    # 2. 프로필은 있지만 닉네임이 없는 경우 수정
    profiles = UserProfile.objects.filter(nickname__isnull=True) | UserProfile.objects.filter(nickname='')
    count = 0
    for profile in profiles:
        profile.nickname = profile.user.username
        profile.save()
        print(f"Updated nickname for user: {profile.user.username}")
        count += 1
        
    print(f"Updated {count} profiles with missing nicknames.")
    print("Done.")

if __name__ == "__main__":
    fix_nicknames()
