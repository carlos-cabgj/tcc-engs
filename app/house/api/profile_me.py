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
        return Response(serializer.data)
    
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
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
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
