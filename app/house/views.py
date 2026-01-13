import os
from django.http import HttpResponse, FileResponse

from django.shortcuts import render


def index(request):
    return HttpResponse("Hello 2")

def auth(request):
    return HttpResponse("Hello 2")

def main(request):
    context = {'name': 'carlos'}
    return render(request, 'house/main.html', context);

def video(request):
    context = {'name': 'carlos'}
    # return render(request, 'house/players/video.html', context);
    print("--------------------") 
    print(os.path.exists('I:/teste.mp4')) 
    return FileResponse(open('I:/teste.mp4', 'rb'), content_type='video/mp4')

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
