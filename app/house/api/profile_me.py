from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from house.serializer import UserProfileSerializer

User = get_user_model()


class ProfileMeView(APIView):
    """API View para obter e atualizar o perfil do usuário autenticado"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self, request):
        """GET: Retorna o perfil do usuário autenticado"""
        user = request.user
        serializer = UserProfileSerializer(user)
        data = serializer.data
        
        # Adicionar URL da foto de perfil se existir
        try:
            if hasattr(user, 'profile') and user.profile.profile_img:
                data['profile_photo'] = request.build_absolute_uri(user.profile.profile_img.url)
            else:
                data['profile_photo'] = None
        except Exception:
            data['profile_photo'] = None
        
        return Response(data)
    
    def put(self, request):
        """PUT: Atualiza completamente o perfil do usuário autenticado"""
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Perfil atualizado com sucesso',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """PATCH: Atualiza parcialmente o perfil do usuário autenticado"""
        user = request.user
        
        # Verificar se está tentando alterar a senha
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if current_password or new_password:
            # Se um dos campos de senha foi preenchido, ambos são obrigatórios
            if not current_password:
                return Response(
                    {'error': 'Senha atual é obrigatória para alterar a senha'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not new_password:
                return Response(
                    {'error': 'Nova senha é obrigatória'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar se a senha atual está correta
            if not user.check_password(current_password):
                return Response(
                    {'error': 'Senha atual incorreta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar tamanho da nova senha
            if len(new_password) < 6:
                return Response(
                    {'error': 'A nova senha deve ter no mínimo 6 caracteres'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Alterar a senha
            user.set_password(new_password)
            user.save()
        
        # Atualizar outros dados do perfil
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            message = 'Perfil atualizado com sucesso'
            if new_password:
                message = 'Perfil e senha atualizados com sucesso'
            
            return Response(
                {
                    'message': message,
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
