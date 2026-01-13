from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    #path("main", views.main, name="main"),
    path("", views.main, name="main"),
    path("video", views.video, name="video"),

    path("auth", views.auth, name="auth"),
    path("api/auth", views.auth, name="auth"),


    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # rota para atualizar token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
