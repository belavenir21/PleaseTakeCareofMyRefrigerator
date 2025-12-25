from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    """사용자 기본 정보 Serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 프로필 Serializer"""
    user = UserSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['user', 'nickname', 'diet_goals', 'created_at', 'updated_at', 'profile_image', 'image_url']
        read_only_fields = ['created_at', 'updated_at', 'image_url']
        extra_kwargs = {
            'profile_image': {'write_only': True}  # 이미지는 업로드용, 조회는 image_url 사용
        }

    def get_image_url(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None

class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입 Serializer"""
    nickname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'nickname']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        nickname = validated_data.pop('nickname')
        user = User.objects.create_user(**validated_data)
        
        # 프로필 생성 (입력받은 닉네임 사용)
        UserProfile.objects.create(user=user, nickname=nickname)
        
        return user

class LoginSerializer(serializers.Serializer):
    """로그인 Serializer"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
