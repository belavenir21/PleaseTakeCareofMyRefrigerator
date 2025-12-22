"""
재료 데이터 JSON 출력
"""
from django.core.management.base import BaseCommand
from refrigerator.models import UserIngredient
from refrigerator.serializers import UserIngredientListSerializer
import json


class Command(BaseCommand):
    help = 'Export ingredient data as JSON for debugging'

    def handle(self, *args, **options):
        # Get first 5 ingredients
        ingredients = UserIngredient.objects.all()[:5]
        serializer = UserIngredientListSerializer(ingredients, many=True)
        
        # Print JSON
        json_data = json.dumps(serializer.data, ensure_ascii=False, indent=2)
        
        with open('ingredient_debug.json', 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        self.stdout.write(self.style.SUCCESS(f'\nData exported to ingredient_debug.json'))
        self.stdout.write(f'Sample ({len(serializer.data)} items):')
        
        for item in serializer.data:
            # ASCII-safe output
            self.stdout.write(f"\n  Name: {item['name']}")
            self.stdout.write(f"  Category: {item['category']}")
            self.stdout.write(f"  Storage: {item['storage_method']}")
