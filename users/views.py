from django.http import HttpResponse

def index(request):
    return HttpResponse("Привет! Это моё первое Django‑приложение.")
