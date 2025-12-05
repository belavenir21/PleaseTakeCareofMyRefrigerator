"""
Management command to create a default user account
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create a default user account (usera)'

    def handle(self, *args, **options):
        username = 'usera'
        email = 'usera@test.com'
        password = 'a1205'
        
        # 기존 사용자 삭제
        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()
            self.stdout.write(
                self.style.WARNING(f'⚠️  기존 사용자 "{username}"를 삭제했습니다.')
            )
        
        # 새 사용자 생성
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ 사용자가 생성되었습니다!\n'
                f'   아이디: {username}\n'
                f'   이메일: {email}\n'
                f'   비밀번호: {password}'
            )
        )
