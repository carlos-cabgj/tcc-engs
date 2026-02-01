from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
import sys

class JWTAuthenticationMiddleware:
    """Middleware que desabilita CSRF para requisições com autenticação JWT"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Debug: mostrar cookies recebidos
        print(f"[Middleware] Path: {request.path}", file=sys.stderr, flush=True)
        print(f"[Middleware] Cookies: {list(request.COOKIES.keys())}", file=sys.stderr, flush=True)
        
        # Se o header Authorization está presente com Bearer token (JWT), marca como CSRF exempt
        if request.META.get('HTTP_AUTHORIZATION', '').startswith('Bearer '):
            request._dont_enforce_csrf_checks = True
            print(f"[Middleware] Token no header encontrado", file=sys.stderr, flush=True)
            
            # Tentar autenticar o usuário
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(request.META.get('HTTP_AUTHORIZATION').split(' ')[1])
                user = jwt_auth.get_user(validated_token)
                request.user = user
                print(f"[Middleware] Usuário autenticado via header: {user.username}", file=sys.stderr, flush=True)
            except (InvalidToken, AuthenticationFailed) as e:
                print(f"[Middleware] Erro ao autenticar via header: {str(e)}", file=sys.stderr, flush=True)
        
        # Se o token está no cookie, adicionar ao header Authorization
        access_token = request.COOKIES.get('access_token')
        if access_token:
            print(f"[Middleware] Token no cookie encontrado: {access_token[:20]}...", file=sys.stderr, flush=True)
            if not request.META.get('HTTP_AUTHORIZATION'):
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
                request._dont_enforce_csrf_checks = True
                print(f"[Middleware] Token do cookie adicionado ao header", file=sys.stderr, flush=True)
                
                # Autenticar o usuário com o token do cookie
                try:
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(access_token)
                    user = jwt_auth.get_user(validated_token)
                    request.user = user
                    print(f"[Middleware] Usuário autenticado via cookie: {user.username}", file=sys.stderr, flush=True)
                except (InvalidToken, AuthenticationFailed) as e:
                    print(f"[Middleware] Erro ao autenticar via cookie: {str(e)}", file=sys.stderr, flush=True)
        else:
            print(f"[Middleware] Nenhum token no cookie", file=sys.stderr, flush=True)
        
        response = self.get_response(request)
        return response
