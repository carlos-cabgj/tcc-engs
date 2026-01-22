"""
URL configuration for cloudunderroof project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

schema_view = get_schema_view(
   openapi.Info(
        title="Minha API",
        default_version='v1',
        description="Documentação da API com Swagger. Para obter token, acesse: /api/token/",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contato@minhaapi.com"),
        license=openapi.License(name="BSD License"),
    ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=(JWTAuthentication,),  # Usar apenas JWT
)

urlpatterns = [
    path("", include("house.urls")),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', csrf_exempt(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
    path('redoc/', csrf_exempt(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

