from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from config.authentication import CsrfExemptSessionAuthentication
import requests
import json

class RecipeChatbotView(APIView):
    """AI 레시피 챗봇 - GMS API 활용"""
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_message = request.data.get('message', '')
        include_ingredients = request.data.get('include_ingredients', False)
        
        if not user_message:
            return Response({'error': '메시지를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        gms_key = getattr(settings, 'GMS_KEY', None)
        if not gms_key:
            return Response({'error': 'AI 서비스가 설정되지 않았습니다.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # 사용자의 보관함 재료 가져오기
        from refrigerator.models import UserIngredient
        user_ingredients = []
        if include_ingredients:
            user_ings = UserIngredient.objects.filter(user=request.user)
            user_ingredients = [ui.name for ui in user_ings]
        
        # 사용자 프로필 정보 (알레르기, 취향)
        from accounts.models import UserProfile
        allergies = []
        diet_goals = ''
        try:
            profile = UserProfile.objects.get(user=request.user)
            allergies = [a.name for a in profile.allergies.all()]
            diet_goals = profile.diet_goals or ''
        except UserProfile.DoesNotExist:
            pass
        
        # 시스템 프롬프트 구성
        system_prompt = """당신은 친절하고 전문적인 요리 어시스턴트입니다. 
사용자의 질문에 맞는 레시피를 추천하고, 요리 팁을 제공합니다.
답변은 친근하고 이해하기 쉽게 작성해주세요.
레시피를 추천할 때는 다음 형식을 사용해주세요:

🍳 **요리 이름**
📝 재료: (재료 목록)
👨‍🍳 조리법:
1. 첫 번째 단계
2. 두 번째 단계
...
💡 팁: (있다면)
"""
        
        # 컨텍스트 정보 추가
        context_info = ""
        if user_ingredients:
            context_info += f"\n\n[사용자의 냉장고 재료]: {', '.join(user_ingredients)}"
        if allergies:
            context_info += f"\n[알레르기 주의]: {', '.join(allergies)} - 이 재료는 피해주세요!"
        if diet_goals:
            context_info += f"\n[식단 목표]: {diet_goals}"
            
        full_prompt = system_prompt + context_info + f"\n\n사용자 질문: {user_message}"
        
        # GMS API 호출
        url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gms_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 2048
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            ai_response = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            if not ai_response:
                ai_response = "죄송합니다, 응답을 생성하지 못했습니다. 다시 시도해주세요."
            
            return Response({
                'message': ai_response,
                'context': {
                    'ingredients_used': user_ingredients if include_ingredients else [],
                    'allergies_considered': allergies,
                }
            })
            
        except requests.exceptions.Timeout:
            return Response({'error': 'AI 응답 시간이 초과되었습니다.'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            return Response({'error': f'AI 서비스 오류: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
