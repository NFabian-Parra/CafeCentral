# cafe_central_project/views.py
from django.shortcuts import render

def home_view(request):
    """
    Vista para la página de inicio del proyecto.
    """
    return render(request, 'home.html', {'project_name': 'CafeCentral'})