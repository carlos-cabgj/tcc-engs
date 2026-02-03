import os
import io
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views.decorators.csrf import csrf_exempt
from house.models import UserProfile, File, Tag
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
import hashlib
from functools import wraps

User = get_user_model()

def jwt_login_required(view_func):
    """Decorador que verifica autenticação por JWT em cookies ou header"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        import sys
        
        # Tentar obter token do cookie ou header
        token = None
        
        # Primeiro tenta header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            print(f"[JWT] Token do header: {token[:20]}...", file=sys.stderr, flush=True)
        
        # Se não achou no header, tenta no cookie
        if not token:
            token = request.COOKIES.get('access_token')
            if token:
                print(f"[JWT] Token do cookie encontrado: {token[:20]}...", file=sys.stderr, flush=True)
            else:
                print(f"[JWT] Cookies disponíveis: {list(request.COOKIES.keys())}", file=sys.stderr, flush=True)
        
        # Se não tem token, redireciona para login com next parameter
        if not token:
            print(f"[JWT] Nenhum token encontrado, redirecionando para login", file=sys.stderr, flush=True)
            # Evitar loop: se já está na página de login, não redirecionar
            if request.path == '/login' or request.path == '/login/':
                return view_func(request, *args, **kwargs)
            # Não adicionar next se for vazio ou a própria página de login
            next_url = request.path if request.path not in ['', '/', '/login', '/login/'] else ''
            if next_url:
                login_url = f'/login?next={next_url}'
            else:
                login_url = '/login'
            return redirect(login_url)
        
        # Tenta validar o token
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            request.user = jwt_auth.get_user(validated_token)
            request.auth = validated_token
            print(f"[JWT] Token válido para: {request.user.username}", file=sys.stderr, flush=True)
        except InvalidToken as e:
            print(f"[JWT] Token inválido: {str(e)}", file=sys.stderr, flush=True)
            # Evitar loop: se já está na página de login, não redirecionar
            if request.path == '/login' or request.path == '/login/':
                # Limpar cookie inválido e continuar para página de login
                response = redirect('/login')
                response.delete_cookie('access_token')
                return response
            next_url = request.path if request.path not in ['', '/', '/login', '/login/'] else ''
            if next_url:
                login_url = f'/login?next={next_url}'
            else:
                login_url = '/login'
            return redirect(login_url)
        except AuthenticationFailed as e:
            print(f"[JWT] Autenticação falhou: {str(e)}", file=sys.stderr, flush=True)
            if request.path == '/login' or request.path == '/login/':
                response = redirect('/login')
                response.delete_cookie('access_token')
                return response
            next_url = request.path if request.path not in ['', '/', '/login', '/login/'] else ''
            if next_url:
                login_url = f'/login?next={next_url}'
            else:
                login_url = '/login'
            return redirect(login_url)
        except Exception as e:
            print(f"[JWT] Erro inesperado: {type(e).__name__} - {str(e)}", file=sys.stderr, flush=True)
            if request.path == '/login' or request.path == '/login/':
                response = redirect('/login')
                response.delete_cookie('access_token')
                return response
            next_url = request.path if request.path not in ['', '/', '/login', '/login/'] else ''
            if next_url:
                login_url = f'/login?next={next_url}'
            else:
                login_url = '/login'
            return redirect(login_url)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


@jwt_login_required
def about(request):
    """View para a página Sobre"""
    return render(request, 'house/about.html')


def index(request):
    return HttpResponse("Hello 2")

def login_view(request):
    """View para exibir a página de login"""
    # Verificar se usuário já está autenticado com token válido
    token = request.COOKIES.get('access_token')
    should_clear_cookie = False
    
    if token:
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            # Token válido, redirecionar para main ou next
            next_url = request.GET.get('next', '/')
            # Evitar loops: se next está vazio ou é login, redirecionar para main
            if not next_url or next_url in ['/login', '/login/', '']:
                next_url = '/'
            return redirect(next_url)
        except (InvalidToken, AuthenticationFailed, Exception) as e:
            # Token inválido, marcar para limpar cookie
            should_clear_cookie = True
            print(f"[LOGIN_VIEW] Token inválido encontrado: {str(e)}", file=sys.stderr, flush=True)
    
    # Verificar se existe algum usuário admin ativo
    admin_group = Group.objects.filter(name__iexact='admin').first()
    
    if admin_group:
        has_active_admin = User.objects.filter(
            groups=admin_group,
            is_active=True
        ).exists()
    else:
        has_active_admin = User.objects.filter(
            is_staff=True,
            is_active=True
        ).exists()
    
    # Se não houver admin ativo, redirecionar para registro inicial
    if not has_active_admin:
        return redirect('initial_setup')
    
    # Buscar todos os usuários ativos para exibir na tela de login
    users = User.objects.filter(is_active=True).select_related('profile').order_by('username')
    
    # Obter o next URL e validar
    next_url = request.GET.get('next', '')
    # Limpar next se for vazio ou inválido
    if next_url in ['', '/', '/login', '/login/']:
        next_url = ''
    
    context = {
        'users': users,
        'next': next_url
    }
    
    response = render(request, 'house/login.html', context)
    
    # Se o token era inválido, limpar o cookie
    if should_clear_cookie:
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        print(f"[LOGIN_VIEW] Cookies inválidos removidos", file=sys.stderr, flush=True)
    
    return response

def initial_setup(request):
    """View para registro do primeiro usuário admin"""
    # Verificar se já existe admin ativo
    admin_group = Group.objects.filter(name__iexact='admin').first()
    
    if admin_group:
        has_active_admin = User.objects.filter(
            groups=admin_group,
            is_active=True
        ).exists()
    else:
        has_active_admin = User.objects.filter(
            is_staff=True,
            is_active=True
        ).exists()
    
    # Se já existe admin, redirecionar para login
    if has_active_admin:
        return redirect('login')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        try:
            # Criar o usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,
                is_active=True
            )
            
            # Criar ou obter grupo Admin
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            user.groups.add(admin_group)
            
            # Criar perfil do usuário
            UserProfile.objects.create(
                user=user,
                bio=f'Administrador do sistema',
                phone=''
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Administrador criado com sucesso! Redirecionando para login...',
                'redirect': '/login'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao criar usuário: {str(e)}'
            }, status=400)
    
    context = {}
    return render(request, 'house/initial_setup.html', context)

@csrf_exempt
def auth(request):
    """View para autenticação que define cookies automaticamente"""
    import sys
    
    if request.method == 'POST':
        import json
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.contrib.auth import authenticate
        from django.http import JsonResponse
        
        try:
            # Obter credenciais
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            print(f"[AUTH] Tentando autenticar: {username}", file=sys.stderr, flush=True)
            
            # Autenticar usuário
            user = authenticate(username=username, password=password)
            
            if user is None:
                print(f"[AUTH] Autenticação falhou para: {username}", file=sys.stderr, flush=True)
                return JsonResponse({'detail': 'Credenciais inválidas'}, status=401)
            
            if not user.is_active:
                print(f"[AUTH] Usuário inativo: {username}", file=sys.stderr, flush=True)
                return JsonResponse({'detail': 'Usuário inativo'}, status=401)
            
            # Gerar tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            print(f"[AUTH] Tokens gerados para: {username}", file=sys.stderr, flush=True)
            
            # Criar resposta com tokens
            response = JsonResponse({
                'access': access_token,
                'refresh': refresh_token
            })
            
            # Definir cookies com tokens
            response.set_cookie(
                'access_token',
                access_token,
                max_age=86400,  # 1 dia
                httponly=False,  # Permitir JavaScript acessar
                samesite='Lax',
                path='/'
            )
            
            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=604800,  # 7 dias
                httponly=False,
                samesite='Lax',
                path='/'
            )
            
            print(f"[AUTH] Cookies definidos para usuário: {username}", file=sys.stderr, flush=True)
            return response
                
        except Exception as e:
            print(f"[AUTH] Erro: {str(e)}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc()
            return JsonResponse({'detail': f'Erro ao autenticar: {str(e)}'}, status=400)
    
    return JsonResponse({'detail': 'Método não permitido'}, status=405)

@jwt_login_required
def main(request):
    from django.db.models import Q
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from house.models import Configuration
    from datetime import datetime
    import re
    import sys
    
    print(f"[MAIN] Usuário autenticado: {request.user.username}", file=sys.stderr, flush=True)
    
    # Verificar grupos do usuário
    user = request.user
    is_admin = user.is_staff or user.groups.filter(name__iexact='admin').exists()
    is_users_group = user.groups.filter(name__iexact='users').exists() or user.groups.filter(name__iexact='usuários').exists()
    is_guest = user.groups.filter(name__iexact='guest').exists()
    
    # Construir query baseado nas permissões
    if is_admin:
        # Admin: vê públicos + users + todos os seus próprios (de qualquer visibilidade)
        files_list = File.objects.filter(
            Q(visibility='public') | 
            Q(visibility='users') | 
            Q(user=user)
        ).order_by('-created_at')
    elif is_users_group:
        # Users: vê públicos + users + todos os seus próprios (de qualquer visibilidade)
        files_list = File.objects.filter(
            Q(visibility='public') | 
            Q(visibility='users') | 
            Q(user=user)
        ).order_by('-created_at')
    elif is_guest:
        # Guest: vê apenas públicos + todos os seus próprios (de qualquer visibilidade)
        files_list = File.objects.filter(
            Q(visibility='public') | 
            Q(user=user)
        ).order_by('-created_at')
    else:
        # Usuário sem grupo: vê apenas seus próprios arquivos
        files_list = File.objects.filter(user=user).order_by('-created_at')
    
    # Aplicar busca se fornecido termo de busca
    search_query = request.GET.get('search', '').strip()
    if search_query:
        search_filters = Q()
        
        # Tentar detectar se é uma data
        date_match = None
        # Formato yyyy-mm-dd
        if re.match(r'^\d{4}-\d{2}-\d{2}$', search_query):
            try:
                date_obj = datetime.strptime(search_query, '%Y-%m-%d').date()
                date_match = date_obj
            except ValueError:
                pass
        # Formato dd/mm/yyyy
        elif re.match(r'^\d{2}/\d{2}/\d{4}$', search_query):
            try:
                date_obj = datetime.strptime(search_query, '%d/%m/%Y').date()
                date_match = date_obj
            except ValueError:
                pass
        
        if date_match:
            # Buscar por data de criação
            search_filters = Q(created_at__date=date_match)
        else:
            # Buscar por nome do arquivo
            search_filters = Q(name__icontains=search_query)
            
            # Buscar por tags
            search_filters |= Q(filetag__tag__name__icontains=search_query)
        
        files_list = files_list.filter(search_filters).distinct()
    
    # Paginação
    page = request.GET.get('page', 1)
    items_per_page = request.GET.get('per_page', 12)  # 12 itens por padrão
    
    paginator = Paginator(files_list, items_per_page)
    
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)
    except EmptyPage:
        files = paginator.page(paginator.num_pages)
    
    # Buscar configuração de extensões
    try:
        ext_files_config = Configuration.objects.get(name='ext_files')
        ext_files = ext_files_config.config
    except Configuration.DoesNotExist:
        ext_files = {}
    
    context = {
        'name': user.username,
        'files': files,
        'ext_files': ext_files,
        'search_query': search_query,
    }
    return render(request, 'house/main.html', context)

@login_required(login_url='login')
def profile_edit(request):
    """View para exibir a página de edição de perfil"""
    context = {
        'user': request.user,
    }
    return render(request, 'house/profile_edit.html', context)

def video(request):
    context = {'name': 'carlos'}
    # return render(request, 'house/players/video.html', context);
    video_path = 'I:/teste.mp4'
    print("--------------------") 
    print(os.path.exists(video_path))
    if os.path.exists(video_path):
        return FileResponse(open(video_path, 'rb'), content_type='video/mp4')
    else:
        return HttpResponse("Video not found", status=404)

def file_list(request):
    xampp_path = 'C:/xampp'
    files = []
    if os.path.exists(xampp_path):
        for item in os.listdir(xampp_path):
            item_path = os.path.join(xampp_path, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                files.append({'name': item, 'path': item_path, 'size': size})
    return render(request, 'file_list.html', {'files': files})

@jwt_login_required
def users_list(request):
    """Lista todos os usuários do sistema - apenas admin"""
    # Verificar se é admin (verificando grupos ou is_staff)
    is_admin = request.user.is_staff or request.user.groups.filter(name__iexact='admin').exists()
    if not is_admin:
        return HttpResponse("Você não tem permissão para acessar esta página", status=403)
    
    users = User.objects.all().prefetch_related('profile')
    context = {'users': users}
    return render(request, 'house/users_list.html', context)

@jwt_login_required
def edit_user(request, user_id):
    """Editar usuário - apenas admin pode editar"""
    # Verificar se é admin (verificando grupos ou is_staff)
    is_admin = request.user.is_staff or request.user.groups.filter(name__iexact='admin').exists()
    if not is_admin:
        return HttpResponse("Você não tem permissão para acessar esta página", status=403)
    
    try:
        user = User.objects.get(id=user_id)
        
        if request.method == 'POST':
            # Atualizar dados do usuário
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.is_active = request.POST.get('is_active') == 'on'
            
            # Atualizar grupos
            group_ids = request.POST.getlist('groups')
            user.groups.set(group_ids)
            
            user.save()
            
            return render(request, 'house/edit_user.html', {
                'user': user,
                'all_groups': Group.objects.all(),
                'success': True,
                'message': 'Usuário atualizado com sucesso!'
            })
        
        # GET - Exibir formulário
        all_groups = Group.objects.all()
        context = {
            'user': user,
            'all_groups': all_groups,
        }
        return render(request, 'house/edit_user.html', context)
    except User.DoesNotExist:
        return HttpResponse("Usuário não encontrado", status=404)

@jwt_login_required
def create_user(request):
    """Criar novo usuário - apenas admin pode criar"""
    # Verificar se é admin (verificando grupos ou is_staff)
    is_admin = request.user.is_staff or request.user.groups.filter(name__iexact='admin').exists()
    if not is_admin:
        return HttpResponse("Você não tem permissão para acessar esta página", status=403)
    
    if request.method == 'POST':
        # Coletando dados do formulário
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        group_ids = request.POST.getlist('groups')
        
        errors = []
        
        # Validações
        if not username:
            errors.append("Nome de usuário é obrigatório")
        elif User.objects.filter(username=username).exists():
            errors.append("Este nome de usuário já está em uso")
        
        if not password:
            errors.append("Senha é obrigatória")
        elif len(password) < 6:
            errors.append("Senha deve ter pelo menos 6 caracteres")
        elif password != password_confirm:
            errors.append("As senhas não correspondem")
        
        if not email:
            errors.append("Email é obrigatório")
        elif User.objects.filter(email=email).exists():
            errors.append("Este email já está em uso")
        
        if not first_name:
            errors.append("Nome é obrigatório")
        
        # Se houver erros, re-exibir formulário
        if errors:
            all_groups = Group.objects.all()
            context = {
                'all_groups': all_groups,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'errors': errors,
            }
            return render(request, 'house/create_user.html', context)
        
        try:
            # Criar novo usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active
            )
            
            # Adicionar aos grupos
            if group_ids:
                user.groups.set(group_ids)
            
            # Redirecionar para lista de usuários com mensagem de sucesso
            return redirect('users_list')
            
        except Exception as e:
            errors.append(f"Erro ao criar usuário: {str(e)}")
            all_groups = Group.objects.all()
            context = {
                'all_groups': all_groups,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'errors': errors,
            }
            return render(request, 'house/create_user.html', context)
    
    # GET - Exibir formulário de criar usuário
    all_groups = Group.objects.all()
    context = {
        'all_groups': all_groups,
    }
    return render(request, 'house/create_user.html', context)

def upload_file(request):
    """Página para upload de arquivos"""
    context = {}
    return render(request, 'house/upload_file.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file_api(request):
    """API para processar upload de arquivo"""
    import uuid
    from PIL import Image
    from django.conf import settings
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    # Validar arquivo
    if 'file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Arquivo não fornecido'})
    
    # Validar nome do arquivo
    file_name = request.POST.get('file_name', '').strip()
    if not file_name:
        return JsonResponse({'success': False, 'error': 'Nome do arquivo não pode estar vazio'})
    
    # Validar visibilidade
    visibility = request.POST.get('visibility', 'users').strip()
    if visibility not in ['public', 'users', 'private']:
        return JsonResponse({'success': False, 'error': 'Visibilidade inválida'})
    
    # Criar pasta do usuário se não existir
    username = request.user.username
    user_upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', username)
    user_thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails', username)
    
    # Criar diretórios se não existirem
    os.makedirs(user_upload_dir, exist_ok=True)
    os.makedirs(user_thumbnail_dir, exist_ok=True)
    
    print(f"DEBUG: Pasta do usuário criada/verificada: {user_upload_dir}")
    
    # Obter arquivo
    uploaded_file = request.FILES['file']
    
    # Gerar signature (hash do arquivo)
    file_signature = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        file_signature.update(chunk)
    signature = file_signature.hexdigest()
    
    # Resetar arquivo para leitura
    uploaded_file.seek(0)
    
    # Gerar UUID v4 para nome do arquivo
    file_uuid = str(uuid.uuid4())
    original_extension = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else ''
    new_file_name = f"{file_uuid}.{original_extension}" if original_extension else file_uuid
    
    # Recriar o arquivo uploaded com novo nome
    uploaded_file.seek(0)
    file_content = uploaded_file.read()
    uploaded_file = InMemoryUploadedFile(
        file=io.BytesIO(file_content),
        field_name='file',
        name=new_file_name,
        content_type=uploaded_file.content_type,
        size=len(file_content),
        charset=None
    )
    
    try:
        # Debug: Log dos dados
        print(f"DEBUG: Arquivo recebido: {uploaded_file.name}, Tamanho: {uploaded_file.size}")
        print(f"DEBUG: Usuário autenticado: {request.user}, ID: {request.user.id}")
        
        # Processar thumbnail se existir
        thumbnail_file = None
        if 'thumbnail' in request.FILES:
            thumbnail_uploaded = request.FILES['thumbnail']
            
            # Validar tipo do thumbnail
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if thumbnail_uploaded.content_type not in allowed_types:
                return JsonResponse({'success': False, 'error': 'Thumbnail deve ser JPG, JPEG, PNG ou WebP'})
            
            try:
                # Abrir imagem e redimensionar se necessário
                img = Image.open(thumbnail_uploaded)
                
                # Aceitar imagens grandes (até 4K) mas redimensionar para 400x400 mantendo proporção
                if img.width > 400 or img.height > 400:
                    # Calcular proporções para manter aspect ratio
                    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                    print(f"DEBUG: Imagem redimensionada para {img.width}x{img.height}")
                
                # Converter para RGB se necessário (para salvar como JPEG)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Criar fundo branco
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Salvar imagem redimensionada em buffer
                thumb_buffer = io.BytesIO()
                img_format = 'JPEG' if thumbnail_uploaded.content_type in ['image/jpeg', 'image/jpg'] else 'PNG'
                img.save(thumb_buffer, format=img_format, quality=85, optimize=True)
                thumb_buffer.seek(0)
                
                # Gerar nome do thumbnail com UUID
                ext = 'jpg' if img_format == 'JPEG' else 'png'
                new_thumb_name = f"{file_uuid}_thumb.{ext}"
                
                # Criar arquivo com thumbnail redimensionado
                thumbnail_file = InMemoryUploadedFile(
                    file=thumb_buffer,
                    field_name='thumbnail',
                    name=new_thumb_name,
                    content_type=f'image/{ext}',
                    size=thumb_buffer.getbuffer().nbytes,
                    charset=None
                )
                
                print(f"DEBUG: Thumbnail processado: {new_thumb_name}, Tamanho final: {img.width}x{img.height}")
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Erro ao processar thumbnail: {str(e)}'})
        
        # Extrair extensão do arquivo original
        extension = original_extension if original_extension else None
        
        # Criar registro no banco
        file_obj = File(
            name=file_name,
            path=uploaded_file.name,
            file=uploaded_file,
            thumbnail=thumbnail_file,
            signature=signature,
            extension=extension,
            size=uploaded_file.size,
            visibility=visibility,
            views_count=0,
            user=request.user,
        )
        file_obj.save()
        
        print(f"DEBUG: Arquivo salvo com ID: {file_obj.id}")
        print(f"DEBUG: File field value: '{file_obj.file}'")
        print(f"DEBUG: File field path: {file_obj.file.path if file_obj.file else 'Vazio'}")
        print(f"DEBUG: File field name: {file_obj.file.name if file_obj.file else 'Vazio'}")
        print(f"DEBUG: Thumbnail: {file_obj.thumbnail.name if file_obj.thumbnail else 'Sem thumbnail'}")
        
        # Processar tags
        tag_ids = request.POST.getlist('tags')
        if tag_ids:
            for tag_id in tag_ids:
                if tag_id.startswith('new_'):
                    # Tag nova - criar
                    tag_name = request.POST.get(f'tag_name_{tag_id}', '')
                    if not tag_name:
                        # Tentar buscar o nome de outra forma (será tratado no frontend)
                        continue
                    tag = Tag.objects.create(
                        name=tag_name,
                        countUses=1,
                        create_by=request.user
                    )
                    file_obj.tags.add(tag)
                else:
                    # Tag existente
                    try:
                        tag = Tag.objects.get(id=tag_id)
                        file_obj.tags.add(tag)
                        # Incrementar countUses
                        tag.countUses += 1
                        tag.save()
                    except Tag.DoesNotExist:
                        pass
        
        # Salvar arquivo no sistema de arquivos (opcional - ajuste conforme necessário)
        # file_path = f"uploads/{file_obj.id}_{uploaded_file.name}"
        # with open(file_path, 'wb') as f:
        #     for chunk in uploaded_file.chunks():
        #         f.write(chunk)
        
        return JsonResponse({
            'success': True,
            'message': 'Arquivo enviado com sucesso',
            'file_id': file_obj.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao salvar arquivo: {str(e)}'
        })


def serve_media_file(request, file_path):
    """
    Serve arquivos de mídia com suporte a Range Requests (necessário para seeking em áudio/vídeo)
    Com validação de permissões baseada na visibilidade do arquivo
    """
    import os
    import mimetypes
    from django.conf import settings
    from django.shortcuts import get_object_or_404
    import sys
    
    print(f"[SERVE_MEDIA] Requisição para: {file_path}", file=sys.stderr, flush=True)
    
    # Fotos de perfil são sempre públicas
    if file_path.startswith('profile_photos/'):
        print(f"[SERVE_MEDIA] Foto de perfil - acesso público", file=sys.stderr, flush=True)
        # Pular validação de permissões para fotos de perfil
    else:
        # Buscar o arquivo no banco de dados
        try:
            # O file_path pode ser do formato: uploads/arquivo.mp3 ou thumbnails/thumb.jpg
            file_obj = File.objects.filter(file__icontains=file_path).first()
            
            if not file_obj:
                # Tentar buscar por thumbnail
                file_obj = File.objects.filter(thumbnail__icontains=file_path).first()
            
            if not file_obj:
                print(f"[SERVE_MEDIA] Arquivo não encontrado no banco: {file_path}", file=sys.stderr, flush=True)
                return HttpResponse('Arquivo não encontrado', status=404)
            
            print(f"[SERVE_MEDIA] Arquivo encontrado: {file_obj.name}, visibilidade: {file_obj.visibility}", file=sys.stderr, flush=True)
            
            # Validar permissões baseadas na visibilidade
            if file_obj.visibility == 'public':
                # Público: todos podem acessar
                print(f"[SERVE_MEDIA] Acesso público permitido", file=sys.stderr, flush=True)
                pass
            
            elif file_obj.visibility == 'users':
                # Users: usuários autenticados podem acessar, exceto guests
                # Verificar autenticação JWT
                token = None
                auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                if not token:
                    token = request.COOKIES.get('access_token')
                
                if not token:
                    print(f"[SERVE_MEDIA] Acesso negado: sem token", file=sys.stderr, flush=True)
                    return HttpResponse('Acesso negado: autenticação necessária', status=403)
                
                # Validar token e obter usuário
                try:
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(token)
                    user = jwt_auth.get_user(validated_token)
                    
                    # Verificar se o usuário não é guest
                    if user.groups.filter(name='guest').exists():
                        print(f"[SERVE_MEDIA] Acesso negado: usuário guest", file=sys.stderr, flush=True)
                        return HttpResponse('Acesso negado: permissão insuficiente', status=403)
                    
                    print(f"[SERVE_MEDIA] Acesso permitido para usuário: {user.username}", file=sys.stderr, flush=True)
                except Exception as e:
                    print(f"[SERVE_MEDIA] Erro ao validar token: {e}", file=sys.stderr, flush=True)
                    return HttpResponse('Acesso negado: token inválido', status=403)
            
            elif file_obj.visibility == 'private':
                # Private: apenas o dono do arquivo pode acessar
                token = None
                auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                if not token:
                    token = request.COOKIES.get('access_token')
                
                if not token:
                    print(f"[SERVE_MEDIA] Acesso negado: sem token (private)", file=sys.stderr, flush=True)
                    return HttpResponse('Acesso negado: autenticação necessária', status=403)
            
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                
                # Verificar se é o dono do arquivo
                if file_obj.user != user:
                    print(f"[SERVE_MEDIA] Acesso negado: não é o dono (user_id={user.id}, owner_id={file_obj.user.id if file_obj.user else None})", file=sys.stderr, flush=True)
                    return HttpResponse('Acesso negado: apenas o proprietário pode acessar', status=403)
                
                print(f"[SERVE_MEDIA] Acesso permitido ao proprietário: {user.username}", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"[SERVE_MEDIA] Erro ao validar token: {e}", file=sys.stderr, flush=True)
                return HttpResponse('Acesso negado: token inválido', status=403)
        
        except Exception as e:
            print(f"[SERVE_MEDIA] Erro ao verificar permissões: {e}", file=sys.stderr, flush=True)
            return HttpResponse('Erro ao verificar permissões', status=500)
    
    # Construir caminho completo do arquivo
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    # Verificar se o arquivo existe no sistema de arquivos
    if not os.path.exists(full_path):
        print(f"[SERVE_MEDIA] Arquivo não existe no sistema: {full_path}", file=sys.stderr, flush=True)
        return HttpResponse('Arquivo não encontrado no sistema', status=404)
    
    # Obter informações do arquivo
    file_size = os.path.getsize(full_path)
    content_type, _ = mimetypes.guess_type(full_path)
    
    print(f"[SERVE_MEDIA] Servindo arquivo: {full_path}, size: {file_size}, type: {content_type}", file=sys.stderr, flush=True)
    
    # Verificar se é uma requisição Range
    range_header = request.META.get('HTTP_RANGE', None)
    
    if range_header:
        # Parse do header Range (formato: bytes=start-end)
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        # Garantir que end não exceda o tamanho do arquivo
        end = min(end, file_size - 1)
        length = end - start + 1
        
        print(f"[SERVE_MEDIA] Range request: {start}-{end}/{file_size}", file=sys.stderr, flush=True)
        
        # Abrir arquivo e ler apenas o range solicitado
        with open(full_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)
        
        # Criar resposta com status 206 Partial Content
        response = HttpResponse(data, status=206, content_type=content_type)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
        
        return response
    else:
        # Requisição normal (sem range)
        response = FileResponse(open(full_path, 'rb'), content_type=content_type)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(file_size)
        
        return response
