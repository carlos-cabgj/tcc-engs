from django.views.decorators.csrf import csrf_exempt

class JWTAuthenticationMiddleware:
    """Middleware que desabilita CSRF para requisições com autenticação JWT"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Se o header Authorization está presente com Bearer token (JWT), marca como CSRF exempt
        if request.META.get('HTTP_AUTHORIZATION', '').startswith('Bearer '):
            request._dont_enforce_csrf_checks = True
        
        # Se o token está no cookie, adicionar ao header Authorization
        access_token = request.COOKIES.get('access_token')
        if access_token and not request.META.get('HTTP_AUTHORIZATION'):
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            request._dont_enforce_csrf_checks = True
        
        response = self.get_response(request)
        return response
