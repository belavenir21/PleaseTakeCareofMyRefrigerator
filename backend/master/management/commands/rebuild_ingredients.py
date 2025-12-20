
import os
import re
import requests
import json
from django.core.management.base import BaseCommand
from master.models import IngredientMaster
from django.db import transaction

class Command(BaseCommand):
    help = '식재료 마스터 데이터를 정제하고 품목별 최적의 이모지를 매핑합니다. (SSAFY GMS 사용 가능)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n--- 🧹 식재료 마스터 최적화 시작 (Emoji & Alias) ---'))
        
        with transaction.atomic():
            self.stdout.write('1. 기존 데이터 초기화...')
            IngredientMaster.objects.all().delete()
            
            # 2. 표준 데이터 및 이모지 정의 (품목별 개별 매핑)
            self.add_standard_data_v3()
            
        self.stdout.write(self.style.SUCCESS('\n--- ✨ 모든 데이터가 완벽하게 복구되었습니다! ---\n'))

    def add_standard_data_v3(self):
        """요청하신 카테고리별로 품목별 최적의 이모지를 매핑하여 등록"""
        
        data_map = {
            '유제품': {
                '우유(Milk, 밀크)': '🥛', '두유': '🫘', '요거트': '🍦', '생크림': '🍰',
                '버터(Butter)': '🧈', '아이스크림': '🍦', '체다치즈': '🧀', '모짜렐라치즈': '🧀',
                '리코타치즈': '🧀', '고다치즈': '🧀', '파마산치즈': '🧀', '까망베르치즈': '🧀',
                '슬라이스치즈': '🧀', '크림치즈': '🧀', '스트링치즈': '🧀', '큐브치즈': '🧀'
            },
            '커피/차': {
                '원두커피(Coffee, 커피)': '🫘', '캡슐커피': '☕', '콜드브루': '☕', '커피음료': '🥤',
                '인스턴트커피': '☕', '보리차': '🍵', '결명자차': '🍵', '옥수수차': '🍵', '현미차': '🍵',
                '둥굴레차': '🍵', '생강차': '🍵', '대추차': '🍵', '유자차': '🍵', '매실차': '🍵',
                '홍차': '☕', '녹차': '🍵', '보이차': '🍵', '허브차': '🌿', '꽃차': '🌸',
                '과일차': '🍎', '밀크티': '🧋', '코코아': '☕', '레몬청': '🍋', '자몽청': '🍊'
            },
            '음료': {
                '생수(Water, 워터)': '💧', '얼음': '🧊', '탄산수': '🫧', '스포츠음료': '🥤',
                '과일음료': '🍹', '야채음료': '🧃', '차음료': '🍵'
            },
            '면/양념/오일': {
                '라면': '🍜', '파스타면': '🍝', '소면': '🍜', '칼국수면': '🍜', '우동면': '🍜',
                '당면': '🍜', '조리용떡': '🍡', '밀가루': '🍞', '부침가루': '🍳', '튀김가루': '🍗',
                '참기름': '🫙', '들기름': '🫙', '식초': '🍶', '소금': '🧂', '설탕': '🍬',
                '간장': '🍶', '고추장': '🏺', '된장': '🏺', '쌈장': '🏺', '굴소스': '🍶',
                '마요네즈': '🍶', '케첩': '🍅', '올리브유': '🫒', '식용유': '🧴', '참깨드레싱': '🥗'
            },
            '간편식/식단': {
                '샐러드': '🥗', '도시락': '🍱', '시리얼': '🥣', '선식': '🥤', '짜장': '🥡',
                '짬뽕': '🍜', '떡볶이': '🥘', '튀김': '🍤', '순대': '🍱', '치킨': '🍗',
                '피자': '🍕', '핫도그': '🌭', '만두': '🥟', '돈까스': '🍱', '함박스테이크': '🍛'
            },
            '육류/달걀': {
                '소고기(Beef, 비프)': '🥩', '돼지고기(Pork, 포크)': '🥩', '양고기': '🍖',
                '닭고기(Chicken, 치킨)': '🍗', '오리고기': '🍗', '달걀(Egg, 에그)': '🥚',
                '가공란': '🥚', '베이컨': '🥓', '소시지': '🌭', '햄': '🍖'
            },
            '수산/건어물': {
                '연어(Salmon)': '🍣', '참치': '🐟', '오징어': '🦑', '낙지': '🐙', '문어': '🐙',
                '전복': '🦪', '새우': '🍤', '게': '🦀', '랍스터': '🦞', '명란': '🍱',
                '김': '🍙', '미역': '🌿', '멸치': '🐟', '황태': '🐟', '고등어': '🐟',
                '갈치': '🐟', '바지락': '🐚', '홍합': '🐚', '굴': '🦪'
            },
            '과일/견과': {
                '사과(Apple)': '🍎', '배': '🍐', '바나나': '🍌', '포도': '🍇', '딸기': '🍓',
                '수박': '🍉', '귤': '🍊', '오렌지': '🍊', '견과류': '🥜', '쌀': '🍚',
                '현미': '🌾', '보리': '🌾', '망고': '🥭', '체리': '🍒', '키위': '🥝'
            },
            '채소': {
                '고구마': '🍠', '감자(Potato, 포태이토)': '🥔', '당근(Carrot)': '🥕',
                '시금치': '🌿', '브로콜리': '🥦', '파프리카': '🫑', '양배추': '🥬',
                '양파(Onion)': '🧅', '대파': '🪴', '마늘(Garlic)': '🧄', '배추': '🥬',
                '오이': '🥒', '호박': '🎃', '고추': '🌶️', '콩나물': '🌱', '숙주': '🌱',
                '상추': '🥬', '깻잎': '🌿', '표고버섯': '🍄', '팽이버섯': '🍄'
            }
        }

        count = 0
        for category, items in data_map.items():
            for name, icon in items.items():
                IngredientMaster.objects.create(
                    name=name,
                    category=category,
                    default_unit='개',
                    icon=icon,
                    api_source='Manual_Perfect'
                )
                count += 1
        
        self.stdout.write(f'   - {count}개의 데이터에 이모지 개별 매핑 완료')

    def ask_gms_emoji(self, name):
        """(선택사항) 리스트에 없는 재료가 생길 경우 SSAFY GMS에 이모지를 물어봅니다."""
        # 이 스크립트에서는 API를 아예 안 써서 크레딧을 아끼도록 설계했습니다.
        # 만약 정말 필요하다면 아래 구조로 호출하면 됩니다.
        gms_key = os.getenv('GMS_KEY')
        if not gms_key:
            return '🍴'
            
        url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gms_key}"
        payload = {
            "contents": [{"parts": [{"text": f"식재료 '{name}'에 가장 어울리는 단일 이모지 1개만 알려줘. 다른 설명 없이 이모지 그 자체만 응답해."}]}]
        }
        try:
            res = requests.post(url, json=payload, timeout=5)
            data = res.json()
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        except:
            return '🍴'
