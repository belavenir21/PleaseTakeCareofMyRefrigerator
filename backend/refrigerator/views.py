from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserIngredient
from .serializers import UserIngredientSerializer, IngredientScanSerializer
from master.models import IngredientMaster
import json
import re
import io
import os
from datetime import date, timedelta
from django.conf import settings
from PIL import Image as PILImage
import numpy as np

class UserIngredientViewSet(viewsets.ModelViewSet):
    """사용자 식재료 뷰셋"""
    queryset = UserIngredient.objects.all()
    serializer_class = UserIngredientSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    def scan(self, request):
        """영수증 스캔 - EasyOCR 사용"""
        serializer = IngredientScanSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            try:
                import easyocr
                image.seek(0)
                img = PILImage.open(image)
                
                print(f'\n🧾 Receipt Scan (EasyOCR)')
                reader = easyocr.Reader(['ko', 'en'], gpu=False)
                img_array = np.array(img)
                results = reader.readtext(img_array)
                
                all_lines = [detection[1].strip() for detection in results]
                
                purchase_date = None
                for line in all_lines[:15]:
                    match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', line)
                    if match:
                        purchase_date = match.group(1)
                        break
                
                detected_items = []
                for line in all_lines:
                    if not re.search(r'[가-힣]', line): continue
                    noise = ['영수증', '카드', '금액', '합계', '전화', '주소', '일자', '과세', '면세']
                    if any(kw in line for kw in noise): continue
                        
                    clean_name = re.sub(r'[^\w\s]', '', line).strip()
                    if len(clean_name) < 2: continue
                    
                    matched_master = IngredientMaster.objects.filter(name__icontains=clean_name[:2])[:1].first()
                    if matched_master:
                        detected_items.append({
                            'name': matched_master.name,
                            'category': matched_master.category,
                            'quantity': 1,
                            'unit': matched_master.default_unit or '개',
                            'icon': matched_master.icon or '📦',
                            'storage_method': '냉장',
                            'expiry_date': (date.today() + timedelta(days=7)).isoformat()
                        })
                
                return Response({'purchase_date': purchase_date, 'items': detected_items})
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], authentication_classes=[])
    def vision(self, request):
        """이미지 인식 - Google Gemini API 사용 (2.0 이상 고정)"""
        serializer = IngredientScanSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            try:
                from google import genai
                from google.genai import types
                
                gemini_key = settings.GOOGLE_GEMINI_API_KEY
                if not gemini_key:
                    return Response({'error': 'GOOGLE_GEMINI_API_KEY가 설정되지 않았습니다.'}, status=500)
                
                client = genai.Client(api_key=gemini_key)
                
                # 1. 사용 가능한 모델 탐색 (2.5 우선)
                try:
                    models = [m.name for m in client.models.list()]
                    print(f'🔍 Available models: {models}')
                    
                    # 오직 2.5 시리즈만 사용 (2.0은 아예 제외)
                    priority_list = [
                        'gemini-2.5-flash-lite', 
                        'gemini-2.5-flash'
                    ]
                    
                    target_model = None
                    for version in priority_list:
                        match = next((m for m in models if version in m), None)
                        if match:
                            target_model = match
                            break
                    
                    if not target_model:
                        # 2.5가 들어간 아무 모델이나 우선 매칭
                        target_model = next((m for m in models if '2.5' in m), 'gemini-2.5-flash-lite')
                except Exception as e:
                    print(f'⚠️ 모델 탐색 실패: {e}')
                    target_model = 'gemini-2.5-flash-lite'
                
                print(f'🎯 Final Selected Model: {target_model}')

                # 2. 이미지 처리
                image.seek(0)
                img = PILImage.open(image)
                if img.width > 1024 or img.height > 1024:
                    img.thumbnail((1024, 1024))
                
                buf = io.BytesIO()
                img.save(buf, format='JPEG', quality=80)
                img_bytes = buf.getvalue()

                # 3. 프롬프트
                prompt = """이미지 속 모든 식재료를 JSON으로 추출하세요. 
가공식품 제외, 원물 식재료 위주.
{"ingredients":[{"name":"재료명","quantity":1,"unit":"개/g"}]}"""

                # 4. API 호출
                try:
                    response = client.models.generate_content(
                        model=target_model,
                        contents=[prompt, types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')]
                    )
                except Exception as api_err:
                    err_msg = str(api_err)
                    if '429' in err_msg:
                        return Response({
                            'error': 'Gemini API 할당량이 초과되었습니다. 1분 후 다시 시도해주세요.',
                            'code': 'QUOTA_EXCEEDED'
                        }, status=429)
                    raise api_err

                res_text = response.text.strip()
                print(f'📝 Extracted: {res_text[:50]}...')

                # 5. 결과 파싱 및 DB 매칭
                json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
                res_data = json.loads(json_match.group()) if json_match else json.loads(res_text)
                
                from difflib import SequenceMatcher
                all_masters = list(IngredientMaster.objects.all())
                final_results = []

                for item in res_data.get('ingredients', []):
                    raw_name = item.get('name', '')
                    best_m = None
                    max_s = 0
                    for m in all_masters:
                        s = SequenceMatcher(None, raw_name, m.name).ratio()
                        if s > max_s:
                            max_s = s
                            best_m = m
                    
                    if best_m and max_s > 0.4:
                        final_results.append({
                            'name': best_m.name,
                            'category': best_m.category,
                            'quantity': item.get('quantity', 1),
                            'unit': best_m.default_unit or item.get('unit', '개'),
                            'icon': best_m.icon or '📦',
                            'storage_method': '냉장',
                            'expiry_date': (date.today() + timedelta(days=7)).isoformat()
                        })
                    else:
                        final_results.append({
                            'name': raw_name,
                            'category': '기타',
                            'quantity': item.get('quantity', 1),
                            'unit': item.get('unit', '개'),
                            'icon': '📦',
                            'storage_method': '냉장',
                            'expiry_date': (date.today() + timedelta(days=7)).isoformat()
                        })

                return Response({'detected_ingredients': final_results})

            except Exception as e:
                import traceback
                traceback.print_exc()
                return Response({'error': str(e)}, status=500)
        return Response(serializer.errors, status=400)