from django.contrib import messages
from django.shortcuts import render

from config.forms import formEmpresas


def inicio(request):
    if not request.user.is_staff:
        messages.error(request, "Não permitido, o usuário deve ser administrativo para acessar esta seção")
        return redirect("main:inicio")
    else:
        return render(request, "config/inicio.html")

def empresas(request):
    if not request.user.is_staff:
        messages.error(request, "Não permitido, o usuário deve ser administrativo para acessar esta seção")
        return redirect("main:inicio")
    else:
        return render(request, "config/empresas.html")
