from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        """Define permissões por ação"""
        if self.action in ['add_first', 'add']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['GET'])  # detail=True = precisa de ID
    def get(self, request, pk=None):  # pk é o ID
        """Obtém usuário por ID"""
        user_id = pk
        return Response({'user_id': user_id})
    
    @action(detail=False, methods=['POST'])
    def add(self, request):
        return Response({2})
    
    @action(detail=False, methods=['POST'])
    def add_first(self, request):
        return Response({1})