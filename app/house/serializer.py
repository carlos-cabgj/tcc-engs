from rest_framework import serializers
from .models import File, UserProfile
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

User = get_user_model()

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

# Backwards compatibility: some code expected `HouseSerializer`
HouseSerializer = FileSerializer


class UserProfileNestedSerializer(serializers.ModelSerializer):
    """Serializer para o perfil do usuário"""
    
    class Meta:
        model = UserProfile
        fields = ['profile_img', 'role', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para editar perfil do usuário com dados do perfil aninhados"""
    
    profile = UserProfileNestedSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'profile',
        ]
    
    def update(self, instance, validated_data):
        """Atualizar dados do usuário"""
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True)

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email', '')
        user = User.objects.create_user(username=username, email=email, password=password)
        # Criar perfil automaticamente
        UserProfile.objects.get_or_create(user=user)
        return user

