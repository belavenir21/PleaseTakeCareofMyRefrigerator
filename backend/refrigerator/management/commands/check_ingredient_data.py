"""
재료 데이터 확인용 management command
"""
from django.core.management.base import BaseCommand
from refrigerator.models import UserIngredient
from master.models import IngredientMaster


class Command(BaseCommand):
    help = 'Check ingredient data and matching'

    def handle(self, *args, **options):
        # 데이터 개수 확인
        user_count = UserIngredient.objects.count()
        master_count = IngredientMaster.objects.count()
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"UserIngredient count: {user_count}")
        self.stdout.write(f"IngredientMaster count: {master_count}")
        self.stdout.write(f"{'='*60}\n")
        
        # UserIngredient 샘플
        self.stdout.write("\n=== UserIngredient Sample (first 10) ===")
        for ing in UserIngredient.objects.all()[:10]:
            master_name = ing.master_ingredient.name if ing.master_ingredient else 'None'
            self.stdout.write(f"  - {ing.name} | master: {master_name}")
        
        # IngredientMaster 샘플
        self.stdout.write("\n=== IngredientMaster Sample (first 15) ===")
        for m in IngredientMaster.objects.all()[:15]:
            self.stdout.write(f"  - {m.name} ({m.category}) {m.icon or 'no-icon'}")
        
        # 매칭 없는 UserIngredient 찾기
        self.stdout.write("\n=== UserIngredients without master_ingredient ===")
        no_master = UserIngredient.objects.filter(master_ingredient__isnull=True)
        self.stdout.write(f"Count: {no_master.count()}")
        for ing in no_master[:10]:
            self.stdout.write(f"  - {ing.name}")
            # 매칭 시도
            master = IngredientMaster.objects.filter(name__icontains=ing.name).first()
            if master:
                self.stdout.write(f"    -> Could match with: {master.name} ({master.category})")
        
        self.stdout.write(self.style.SUCCESS('\nCheck completed!'))
