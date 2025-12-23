from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Fix missing nicknames in user profiles'

    def handle(self, *args, **options):
        self.stdout.write('Starting nickname fix...')
        
        # 1. 프로필이 없는 유저에게 프로필 생성
        created_count = 0
        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, nickname=user.username)
                self.stdout.write(f"Created profile for {user.username}")
                created_count += 1
        
        self.stdout.write(f"Created {created_count} profiles")
        
        # 2. 닉네임이 비어있는 프로필 수정
        updated_count = 0
        profiles_to_fix = UserProfile.objects.filter(nickname__isnull=True) | UserProfile.objects.filter(nickname='')
        
        for profile in profiles_to_fix:
            profile.nickname = profile.user.username
            profile.save()
            self.stdout.write(f"Updated nickname for {profile.user.username}")
            updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Done! Created {created_count} profiles, updated {updated_count} nicknames'))
