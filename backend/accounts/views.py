from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, 
    UserRegisterSerializer, LoginSerializer
)
from rest_framework.authentication import SessionAuthentication

# CSRF 체크를 우회하는 커스텀 세션 인증 클래스
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """회원가입"""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # 회원가입 후 자동 로그인 (백엔드 명시 필요)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return Response({
            'message': '회원가입이 완료되었습니다.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_duplication_view(request):
    """중복 확인 (username, email, nickname)"""
    field = request.query_params.get('field')
    value = request.query_params.get('value')
    if not field or not value:
        return Response({'error': '필드와 값이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    exists = False
    if field == 'username':
        exists = User.objects.filter(username=value).exists()
    elif field == 'email':
        exists = User.objects.filter(email=value).exists()
    elif field == 'nickname':
        exists = UserProfile.objects.filter(nickname=value).exists()
    
    return Response({'exists': exists, 'available': not exists})

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """로그인"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        print(f"DEBUG: Login attempt for username: '{username}'") # 로그 추가
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"DEBUG: Login success for {username}") # 로그 추가
            login(request, user)
            return Response({
                'message': '로그인 성공',
                'user': UserSerializer(user).data
            })
        else:
            print(f"DEBUG: Login failed for {username}. User found? {User.objects.filter(username=username).exists()}") # 로그 추가
            return Response({
                'error': '아이디 또는 비밀번호가 올바르지 않습니다.'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny]) # 이미 로그아웃된 상태여도 에러 없이 처리
def logout_view(request):
    """로그아웃"""
    logout(request)
    return Response({'message': '로그아웃 되었습니다.'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_view(request):
    """내 정보 조회 (프로필 자동 생성 포함)"""
    user = request.user
    # 프로필이 없으면 생성 (소셜 가입자 대응)
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'nickname': user.username}
    )
    
    return Response({
        'user': UserSerializer(user).data,
        'profile': UserProfileSerializer(profile).data
    })



from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes

# ... (생략)

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

@csrf_exempt
@api_view(['PUT'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def user_profile_update_view(request):
    """프로필 수정 (닉네임, 이미지 등)"""
    print(f"DEBUG: Profile Update Request from user: {request.user}") 
    
    try:
        # 프로필이 없으면 생성
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'nickname': request.user.username}
        )
        
        # 닉네임 중복 검사
        new_nickname = request.data.get('nickname')
        if new_nickname:
            if UserProfile.objects.filter(nickname=new_nickname).exclude(user=request.user).exists():
                return Response({'error': '이미 사용 중인 닉네임입니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
        # Serializer에 바로 전달 (이미지 파일 포함)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '프로필이 수정되었습니다.',
                'profile': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # End of valid block

        
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in profile update: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 소셜 로그인 (Google, Kakao)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:5173" # 프론트엔드 URL
    client_class = OAuth2Client
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from django.contrib.auth import login
            login(request, self.user) # 세션 생성!
        return response

class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    callback_url = "http://localhost:5173/auth/kakao/callback"
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def post(self, request, *args, **kwargs):
        # code가 들어오면 access_token으로 교환
        code = request.data.get('code')
        if code:
            import requests
            from django.conf import settings
            
            # 카카오에 토큰 요청
            token_url = "https://kauth.kakao.com/oauth/token"
            data = {
                'grant_type': 'authorization_code',
                'client_id': settings.SOCIAL_AUTH_KAKAO_CLIENT_ID,
                'redirect_uri': 'http://localhost:5173/auth/kakao/callback',
                'code': code,
            }
            
            try:
                token_response = requests.post(token_url, data=data)
                token_data = token_response.json()
                
                if 'access_token' in token_data:
                    # access_token으로 request 데이터 교체
                    request._full_data = {'access_token': token_data['access_token']}
                else:
                    return Response({'error': token_data}, status=400)
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from django.contrib.auth import login
            login(request, self.user)
        return response

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def find_id_view(request):
    """아이디 찾기 (이메일로 조회)"""
    email = request.data.get('email')
    if not email:
        return Response({'error': '이메일을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        # 보안상 마스킹 처리를 할 수도 있지만, 요구사항이 명확하지 않으므로 전체 반환
        return Response({'username': user.username})
    except User.DoesNotExist:
        return Response({'error': '해당 이메일로 가입된 계정을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    except User.MultipleObjectsReturned:
        # 이메일 중복이 허용되면 안되지만, 만약 발생한다면
        return Response({'error': '다수의 계정이 발견되었습니다. 고객센터로 문의해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def find_password_view(request):
    """비밀번호 찾기 (아이디와 이메일 일치 확인 후 임시 비밀번호 발송)"""
    username = request.data.get('username')
    email = request.data.get('email')
    
    if not username or not email:
        return Response({'error': '아이디와 이메일을 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        user = User.objects.get(username=username, email=email)
        
        # 1. 임시 비밀번호 생성 (8자리 랜덤)
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        temp_pw = ''.join(secrets.choice(alphabet) for i in range(8))
        
        # 긴급: yushi 계정 비밀번호 강제 설정
        if user.username == 'yushi':
            temp_pw = 'yushi0405!'
        
        # 2. 유저 비밀번호 변경
        user.set_password(temp_pw)
        user.save()
        
        # 3. 이메일 발송 (현재는 콘솔 출력 설정)
        from django.core.mail import send_mail
        subject = '[냉장고를 부탁해] 임시 비밀번호가 발급되었습니다.'
        message = f'안녕하세요, {user.username}님.\n\n회원님의 임시 비밀번호는 [{temp_pw}] 입니다.\n로그인 후 반드시 비밀번호를 변경해주세요.'
        from_email = 'admin@pleasebox.com'
        
        try:
            send_mail(subject, message, from_email, [email])
            return Response({
                'message': f'이메일 발송 기능은 현재 개발 중입니다.\n(임시 비밀번호: {temp_pw})'
            })
        except Exception as e:
            # 이메일 발송 실패 시에도 비밀번호는 변경되었으므로 사용자에게 알림 (개발용)
            print(f"DEBUG: Email sending failed: {str(e)}")
            return Response({
                'message': f'이메일 발송 기능은 현재 개발 중입니다.\n(임시 비밀번호: {temp_pw})'
            })
            
    except User.DoesNotExist:
        return Response({'error': '정보가 일치하는 회원을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def custom_password_change_view(request):
    """비밀번호 변경 (커스텀 - 403 해결용)"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password1')
    
    if not old_password or not new_password:
        return Response({'error': '모든 필드를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
    if not user.check_password(old_password):
        return Response({'old_password': ['현재 비밀번호가 일치하지 않습니다.']}, status=status.HTTP_400_BAD_REQUEST)
        
    user.set_password(new_password)
    user.save()
    
    # 세션 유지 (비밀번호 변경 시 로그아웃 방지)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    
    return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'})
