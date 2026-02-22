from django.core.management.base import BaseCommand
from recipes.models import Recipe

class Command(BaseCommand):
    help = 'Delete specific recipe'

    def handle(self, *args, **kwargs):
        # 김치볶음밥 레시피 찾기 및 삭제
        recipes = Recipe.objects.filter(title__icontains='김치볶음밥')
        self.stdout.write(f"Found {recipes.count()} recipes:")
        for r in recipes:
            self.stdout.write(f"  - ID: {r.id}, Title: {r.title}, Author: {r.author}")
            r.delete()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Deleted!"))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Done!'))
