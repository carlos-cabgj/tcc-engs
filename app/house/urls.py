from django.urls import path, include, re_path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views
from .api.register import RegisterView
from .api.profile_me import ProfileMeView
from rest_framework.routers import DefaultRouter
from .api.user import UserViewSet
from .api.profile import ProfileViewSet
from .api.tags import TagViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    #path("", views.index, name="index"),
    #path("main", views.main, name="main"),
    path("", views.main, name="main"),
    path("about", views.about, name="about"),
    path("video", views.video, name="video"),
    path("profile", views.profile_edit, name="profile_edit"),
    path("users", views.users_list, name="users_list"),
    path("users/create/", views.create_user, name="create_user"),
    path("users/<int:user_id>/edit/", views.edit_user, name="edit_user"),
    path("upload", views.upload_file, name="upload_file"),
    path("api/upload/", views.upload_file_api, name="upload_file_api"),
    
    # Servir arquivos de mídia com suporte a Range Requests
    re_path(r'^media/(?P<file_path>.+)$', views.serve_media_file, name='serve_media'),
    
    path("login", views.login_view, name="login"),
    path("initial-setup", views.initial_setup, name="initial_setup"),

    path("auth", views.auth, name="auth"),
    path("api/auth", views.auth, name="auth"),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # rota para atualizar token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # rota para registrar usuário (criar usuário com senha)
    path('api/register/', RegisterView.as_view(), name='register'),
    
    # rota para obter e atualizar perfil do usuário autenticado - DEVE vir antes do router
    path('api/profile/me/', ProfileMeView.as_view(), name='profile-me'),

    # router com outras rotas dinâmicas
    path('api/', include(router.urls)),
]
