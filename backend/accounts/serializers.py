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
    
    class Meta:
        model = UserProfile
        fields = ['user', 'nickname', 'diet_goals', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입 Serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # 프로필 자동 생성
        UserProfile.objects.create(user=user, nickname=user.username)
        
        return user

class LoginSerializer(serializers.Serializer):
    """로그인 Serializer"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
