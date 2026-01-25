import os
import io
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import InMemoryUploadedFile
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
        # Tentar obter token do cookie ou header
        token = None
        
        # Primeiro tenta header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Se não achou no header, tenta no cookie
        if not token:
            token = request.COOKIES.get('access_token')
        
        # Se não tem token, redireciona para login
        if not token:
            return redirect('login')
        
        # Tenta validar o token
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            request.user = jwt_auth.get_user(validated_token)
            request.auth = validated_token
        except (InvalidToken, AuthenticationFailed):
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def index(request):
    return HttpResponse("Hello 2")

def login_view(request):
    """View para exibir a página de login"""
    context = {}
    return render(request, 'house/login.html', context)

def auth(request):
    return HttpResponse("Hello 2")

def main(request):
    context = {'name': 'carlos'}
    return render(request, 'house/main.html', context);

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
    
    # Obter arquivo
    uploaded_file = request.FILES['file']
    
    # Gerar signature (hash do arquivo)
    file_signature = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        file_signature.update(chunk)
    signature = file_signature.hexdigest()
    
    # Resetar arquivo para leitura
    uploaded_file.seek(0)
    
    # Recriar o arquivo uploaded para garantir que está pronto para salvar
    uploaded_file.seek(0)
    file_content = uploaded_file.read()
    uploaded_file = InMemoryUploadedFile(
        file=io.BytesIO(file_content),
        field_name='file',
        name=uploaded_file.name,
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
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
            if thumbnail_uploaded.content_type not in allowed_types:
                return JsonResponse({'success': False, 'error': 'Thumbnail deve ser JPG, JPEG ou PNG'})
            
            # Validar dimensões
            from PIL import Image
            try:
                img = Image.open(thumbnail_uploaded)
                if img.width > 400 or img.height > 400:
                    return JsonResponse({'success': False, 'error': 'Thumbnail deve ter no máximo 400x400 pixels'})
                
                # Renomear thumbnail com signature_thumb.extensao
                ext = thumbnail_uploaded.name.split('.')[-1].lower()
                new_thumb_name = f"{signature}_thumb.{ext}"
                
                # Recriar arquivo com novo nome
                thumbnail_uploaded.seek(0)
                thumb_content = thumbnail_uploaded.read()
                thumbnail_file = InMemoryUploadedFile(
                    file=io.BytesIO(thumb_content),
                    field_name='thumbnail',
                    name=new_thumb_name,
                    content_type=thumbnail_uploaded.content_type,
                    size=len(thumb_content),
                    charset=None
                )
                
                print(f"DEBUG: Thumbnail processado: {new_thumb_name}")
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Erro ao processar thumbnail: {str(e)}'})
        
        # Criar registro no banco
        file_obj = File(
            name=file_name,
            path=uploaded_file.name,
            file=uploaded_file,
            thumbnail=thumbnail_file,
            signature=signature,
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
