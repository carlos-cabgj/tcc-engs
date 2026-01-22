from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from house.serializer import UserProfileSerializer

User = get_user_model()


class ProfileViewSet(viewsets.ViewSet):
    """ViewSet para gerenciar o perfil do usuário (agora usando User model estendido)"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['GET', 'PUT', 'PATCH'])
    def me(self, request):
        """
        GET: Retorna o perfil do usuário autenticado
        PUT/PATCH: Atualiza o perfil do usuário autenticado
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = UserProfileSerializer(
                user,
                data=request.data,
                partial=(request.method == 'PATCH')
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'message': 'Perfil atualizado com sucesso',
                        'data': serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
