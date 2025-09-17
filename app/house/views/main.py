from django.http import HttpResponse, render


def main(request):
    context = {'name': 'carlos'}
    return render(request, 'template/house/main.html', context);