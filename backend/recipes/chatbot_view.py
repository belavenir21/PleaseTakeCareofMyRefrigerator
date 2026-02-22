"""
AI 레시피 챗봇 View - V2
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from config.authentication import CsrfExemptSessionAuthentication
from .ai_services import get_chatbot_response


class RecipeChatbotView(APIView):
    """AI 레시피 챗봇"""
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message', '')
        include_ingredients = request.data.get('include_ingredients', False)

        if not user_message:
            return Response(
                {'error': '메시지를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = get_chatbot_response(
                message=user_message,
                user=request.user,
                include_ingredients=include_ingredients
            )
            return Response(result)
        except Exception as e:
            error_msg = str(e)
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "API 키" in error_msg or "한도" in error_msg or "토큰" in error_msg else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(
                {'error': error_msg},
                status=status_code
            )
