from rest_framework import serializers
from .models import File, UserProfile, Tag
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.validators import UniqueValidator
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

User = get_user_model()

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

# Backwards compatibility: some code expected `HouseSerializer`
HouseSerializer = FileSerializer


class TagSerializer(serializers.ModelSerializer):
    """Serializer para listar tags"""
    create_by_username = serializers.CharField(source='create_by.username', read_only=True)
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'countUses', 'created_at', 'updated_at', 'lastUsed_at', 'create_by', 'create_by_username']
        read_only_fields = ['id', 'countUses', 'created_at', 'updated_at', 'lastUsed_at', 'create_by_username']


class TagCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar tags - apenas 'name' é esperado"""
    
    class Meta:
        model = Tag
        fields = ['name']
    
    def create(self, validated_data):
        """Criar tag com create_by do usuário autenticado e countUses=0"""
        tag = Tag.objects.create(
            name=validated_data['name'],
            countUses=0,
            create_by=self.context['request'].user,
            updated_at=timezone.now(),
            lastUsed_at=timezone.now(),
        )
        return tag


class UserProfileNestedSerializer(serializers.ModelSerializer):
    """Serializer para o perfil do usuário"""
    
    class Meta:
        model = UserProfile
        fields = ['profile_img', 'role', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para editar perfil do usuário com dados do perfil aninhados"""
    
    profile = UserProfileNestedSerializer(read_only=True)
    profile_photo = serializers.ImageField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'profile',
            'profile_photo',
        ]
    
    def update(self, instance, validated_data):
        """Atualizar dados do usuário e perfil"""
        # Extrair foto do perfil se fornecida
        profile_photo = validated_data.pop('profile_photo', None)
        
        # Atualizar dados do usuário
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        
        # Atualizar foto do perfil se fornecida
        if profile_photo is not None:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            
            # Processar e redimensionar a imagem para 400x400
            img = Image.open(profile_photo)
            
            # Verificar se tem transparência
            has_transparency = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
            
            # Converter P para RGBA se tiver transparência
            if img.mode == 'P' and has_transparency:
                img = img.convert('RGBA')
            elif img.mode not in ('RGB', 'RGBA', 'LA'):
                img = img.convert('RGB')
            
            # Redimensionar mantendo proporção
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Criar um canvas 400x400 e centralizar a imagem
            if has_transparency:
                # Manter transparência para PNG
                output_img = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
                offset_x = (400 - img.width) // 2
                offset_y = (400 - img.height) // 2
                output_img.paste(img, (offset_x, offset_y), mask=img if img.mode == 'RGBA' else None)
                format_type = 'PNG'
                file_ext = 'png'
                mime_type = 'image/png'
            else:
                # Fundo branco para JPEG
                output_img = Image.new('RGB', (400, 400), (255, 255, 255))
                offset_x = (400 - img.width) // 2
                offset_y = (400 - img.height) // 2
                output_img.paste(img, (offset_x, offset_y))
                format_type = 'JPEG'
                file_ext = 'jpg'
                mime_type = 'image/jpeg'
            
            # Salvar em buffer
            output = BytesIO()
            if format_type == 'JPEG':
                output_img.save(output, format=format_type, quality=85)
            else:
                output_img.save(output, format=format_type, optimize=True)
            output.seek(0)
            
            # Criar novo arquivo
            profile.profile_img = InMemoryUploadedFile(
                output, 'ImageField',
                f"{profile_photo.name.split('.')[0]}.{file_ext}",
                mime_type,
                sys.getsizeof(output), None
            )
            profile.save()
        
        return instance

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True)
    group = serializers.CharField(required=False, allow_blank=True)

    def validate_group(self, value):
        """Validar se o grupo existe na tabela auth_group"""
        if value:  # Se um grupo foi fornecido
            try:
                Group.objects.get(name=value)
            except Group.DoesNotExist:
                raise serializers.ValidationError(
                    f"O grupo '{value}' não existe. Por favor, forneça um grupo válido."
                )
        return value

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email', '')
        group_name = validated_data.get('group')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Criar perfil automaticamente
        UserProfile.objects.get_or_create(user=user)
        
        # Atribuir grupo se fornecido
        if group_name:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        
        return user

