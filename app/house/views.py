import os
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from house.models import UserProfile, File
import hashlib

User = get_user_model()


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

def users_list(request):
    """Lista todos os usuários do sistema"""
    users = User.objects.all().prefetch_related('profile')
    context = {'users': users}
    return render(request, 'house/users_list.html', context)

def edit_user(request, user_id):
    """Editar usuário - será implementado"""
    try:
        user = User.objects.get(id=user_id)
        context = {'user': user}
        return render(request, 'house/edit_user.html', context)
    except User.DoesNotExist:
        return HttpResponse("Usuário não encontrado", status=404)

def upload_file(request):
    """Página para upload de arquivos"""
    context = {}
    return render(request, 'house/upload_file.html', context)

@login_required(login_url='login')
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
    
    try:
        # Criar registro no banco
        file_obj = File.objects.create(
            name=file_name,
            path=uploaded_file.name,
            signature=signature,
            size=uploaded_file.size,
            visibility=visibility,
            views_count=0,
        )
        
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
