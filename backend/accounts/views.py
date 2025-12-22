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
@permission_classes([IsAuthenticated])
def logout_view(request):
    """로그아웃"""
    logout(request)
    return Response({'message': '로그아웃 되었습니다.'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_view(request):
    """내 정보 조회"""
    user = request.user
    profile = UserProfile.objects.get(user=user)
    
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
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
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
