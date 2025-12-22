import time
import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from master.models import IngredientMaster

class Command(BaseCommand):
    help = 'Gemini AI를 사용하여 식재료 아이콘(이모지)을 업데이트합니다.'

    def handle(self, *args, **options):
        gms_key = getattr(settings, 'GMS_KEY', None)
        if not gms_key:
            self.stdout.write(self.style.ERROR('GMS_KEY가 설정되지 않았습니다.'))
            return

        url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gms_key}"
        
        # 전체 재료 가져오기
        ingredients = list(IngredientMaster.objects.all().order_by('id'))
        total = len(ingredients)
        batch_size = 50
        
        self.stdout.write(f"총 {total}개의 식재료 아이콘 업데이트를 시작합니다...")

        for i in range(0, total, batch_size):
            batch = ingredients[i:i+batch_size]
            names = [ing.name for ing in batch]
            
            self.stdout.write(f"\nProcessing batch {i//batch_size + 1}/{(total-1)//batch_size + 1} ({len(batch)} items)...")

            prompt = f"""
            Task: Assign the single most appropriate emoji for each Korean food ingredient listed below.
            
            Rules:
            1. Response must be a valid JSON object: {{"Ingredient Name": "Emoji"}}
            2. Choose emojis based on visual similarity or main ingredient category.
            3. Accuracy visual is priority.
               - "대파" (Green Onion) -> 🥬 or 🎋 (Not Onion 🧅)
               - "두부" (Tofu) -> 🧊 or ⬜ (Not Rice 🌾)
               - "콜라비" (Kohlrabi) -> 🟣 or 🥬 (Not Cola 🥤)
               - "부침가루" (Flour) -> 🥡 or ⚪
               - "고등어" (Mackerel) -> 🐟
            4. Do NOT include markdown formatting. Just raw JSON.
            
            Ingredients:
            {json.dumps(names, ensure_ascii=False)}
            """

            try:
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                response = requests.post(url, json=payload, timeout=40)
                
                if response.status_code == 200:
                    result = response.json()
                    try:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        text = text.replace('```json', '').replace('```', '').strip()
                        emoji_map = json.loads(text)
                        
                        updated_count = 0
                        for ing in batch:
                            new_icon = emoji_map.get(ing.name)
                            if new_icon and new_icon != ing.icon:
                                # 이모지 유효성 간단 체크 (길이 등)? 일단 패스
                                ing.icon = new_icon
                                ing.save()
                                updated_count += 1
                        
                        self.stdout.write(self.style.SUCCESS(f"  Batch complete: {updated_count} icons updated."))
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Parsing Error: {str(e)}"))
                else:
                    self.stdout.write(self.style.ERROR(f"  API Error: {response.status_code}"))
                    
                time.sleep(0.5) 
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Request Error: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('All icons updated successfully!'))
