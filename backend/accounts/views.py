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
        # 회원가입 후 자동 로그인
        login(request, user)
        return Response({
            'message': '회원가입이 완료되었습니다.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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



@csrf_exempt
@api_view(['PUT'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def user_profile_update_view(request):
    """프로필 수정 (닉네임 중복 검사 포함)"""
    print(f"DEBUG: Profile Update Request from user: {request.user}") # 디버깅 로그
    print(f"DEBUG: Request Data: {request.data}") 
    print(f"DEBUG: Auth Classes: {request.authenticators}")

    try:
        # 프로필이 없으면 생성 (안정성 강화)
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'nickname': request.user.username}
        )
        
        # 닉네임 중복 검사
        new_nickname = request.data.get('nickname')
        if new_nickname:
            if UserProfile.objects.filter(nickname=new_nickname).exclude(user=request.user).exists():
                print("DEBUG: Nickname duplicate")
                return Response({'error': '이미 사용 중인 닉네임입니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
        # 필요한 데이터만 추출
        update_data = {}
        if 'nickname' in request.data:
            update_data['nickname'] = request.data['nickname']
        if 'diet_goals' in request.data:
            update_data['diet_goals'] = request.data['diet_goals']

        serializer = UserProfileSerializer(profile, data=update_data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            print("DEBUG: Profile Updated Successfully")
            return Response({
                'message': '프로필이 수정되었습니다.',
                'profile': serializer.data
            })
        
        print(f"DEBUG: Serializer Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
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
    """비밀번호 찾기 (아이디와 이메일 일치 확인)"""
    username = request.data.get('username')
    email = request.data.get('email')
    
    if not username or not email:
        return Response({'error': '아이디와 이메일을 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        user = User.objects.get(username=username, email=email)
        # 실제 서비스라면: 임시 비밀번호 생성 후 이메일 발송
        # 현재 데모 환경에서는 성공 메시지만 반환
        return Response({
            'message': '확인되었습니다. (이메일 발송 시스템이 연동되지 않아, 관리자에게 비밀번호 초기화를 요청해주세요.)'
        })
    except User.DoesNotExist:
        return Response({'error': '정보가 일치하는 회원을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
