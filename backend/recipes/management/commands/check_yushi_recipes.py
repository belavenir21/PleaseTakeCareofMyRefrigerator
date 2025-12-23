from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recipes.models import Recipe

class Command(BaseCommand):
    help = 'Check and update recipes for user yushi'

    def handle(self, *args, **kwargs):
        try:
            # yushi 사용자 확인
            user = User.objects.get(username='yushi')
            nickname = user.profile.nickname if hasattr(user, 'profile') and user.profile else 'No profile'
            self.stdout.write(f"User: {user.username}, Nickname: {nickname}")
            
            # yushi가 만든 레시피 확인
            user_recipes = Recipe.objects.filter(author=user)
            self.stdout.write(f"\nYushi's recipes: {user_recipes.count()}")
            for r in user_recipes[:10]:
                self.stdout.write(f"  - {r.id}: {r.title} (api_source: {r.api_source})")
            
            # api_source가 'user' 또는 'ai_generated'인데 author가 없는 레시피 확인
            no_author_recipes = Recipe.objects.filter(
                api_source__in=['user', 'ai_generated'], 
                author__isnull=True
            )
            self.stdout.write(f"\nUser/AI recipes without author: {no_author_recipes.count()}")
            for r in no_author_recipes[:10]:
                self.stdout.write(f"  - {r.id}: {r.title} (api_source: {r.api_source})")
            
            # yushi를 author로 설정 (확인 후)
            if no_author_recipes.exists():
                self.stdout.write(self.style.WARNING(f"\nFound {no_author_recipes.count()} recipes without author."))
                response = input("Set yushi as author for all user/AI recipes? (yes/no): ")
                if response.lower() == 'yes':
                    updated = no_author_recipes.update(author=user)
                    self.stdout.write(self.style.SUCCESS(f"Updated {updated} recipes with author: {nickname}"))
                else:
                    self.stdout.write("Skipped author update.")
            else:
                self.stdout.write(self.style.SUCCESS("All user/AI recipes have authors!"))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User 'yushi' not found"))
