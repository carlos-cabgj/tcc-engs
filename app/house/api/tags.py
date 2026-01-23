from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from house.models import Tag
from house.serializer import TagSerializer, TagCreateSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar e gerenciar tags com filtros de ordenação e busca.
    Apenas usuários autenticados podem acessar.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['countUses', 'lastUsed_at', 'created_at', 'updated_at']
    ordering = ['-created_at']  # Ordenação padrão
    
    def get_queryset(self):
        """Filtrar tags excluindo deletadas (deleted_at não nulo)"""
        queryset = Tag.objects.filter(deleted_at__isnull=True)
        
        # Filtro de 'novo' (últimas N horas/dias)
        novo = self.request.query_params.get('novo', None)
        if novo:
            try:
                horas = int(novo)
                from datetime import timedelta
                from django.utils import timezone
                data_limite = timezone.now() - timedelta(hours=horas)
                queryset = queryset.filter(created_at__gte=data_limite)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_serializer_class(self):
        """Usar serializer diferente para criação"""
        if self.action == 'create':
            return TagCreateSerializer
        return TagSerializer
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/tags/ - Criar nova tag
        Body: { "name": "nome-da-tag" }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Retornar a tag criada com o serializer padrão
        tag = serializer.instance
        response_serializer = TagSerializer(tag)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['GET'])
    def populares(self, request):
        """
        Retorna as tags mais usadas (ordenadas por countUses)
        Query params:
        - limit: número de tags a retornar (default: 10)
        """
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 10
        
        tags = self.get_queryset().order_by('-countUses')[:limit]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def recentes_usadas(self, request):
        """
        Retorna as tags usadas mais recentemente
        Query params:
        - limit: número de tags a retornar (default: 10)
        """
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 10
        
        tags = self.get_queryset().order_by('-lastUsed_at')[:limit]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)
