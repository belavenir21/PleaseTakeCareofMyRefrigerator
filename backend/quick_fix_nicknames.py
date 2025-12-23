from django.contrib.auth.models import User
from accounts.models import UserProfile

def fix_nicknames():
    print("Starting nickname fix...")
    
    # 1. 프로필이 없는 유저에게 프로필 생성
    users_without_profile = []
    for user in User.objects.all():
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user, nickname=user.username)
            users_without_profile.append(user.username)
            print(f"Created profile for {user.username}")
    
    print(f"Created {len(users_without_profile)} profiles")
    
    # 2. 닉네임이 비어있는 프로필 수정
    null_nicknames = UserProfile.objects.filter(nickname__isnull=True)
    empty_nicknames = UserProfile.objects.filter(nickname='')
    
    for profile in null_nicknames | empty_nicknames:
        profile.nickname = profile.user.username
        profile.save()
        print(f"Updated nickname for {profile.user.username}")
    
    print("Done!")

fix_nicknames()
