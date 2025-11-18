from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm

from api.services import procesar_carga_masiva, generar_plantilla_excel
from api.forms import CargaMasivaForm
from api.models import CalificacionTributaria


# ===============================
# Vistas de Autenticación Web
# ===============================
def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta creada correctamente. Ya puedes iniciar sesión.")
            return redirect("accounts:login")
    else:
        form = UserCreationForm()
    return render(request, "accounts/registro.html", {"form": form})


def mi_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("accounts:home")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


@login_required
def mi_logout(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("accounts:login")


# ===============================
# Dashboard / Home
# ===============================
@login_required
def home(request):
    return render(request, "home.html")


# ===============================
# Cargas Masivas
# ===============================
@login_required
def lista_cargas(request):
    return render(request, "accounts/lista_cargas.html")


@login_required
def nueva_carga(request):
    from api.excel_handler import ExcelHandler  # Import directo

    if request.method == "POST":
        form = CargaMasivaForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            tipo_carga = form.cleaned_data["tipo_carga"]
            mercado = form.cleaned_data["mercado"]

            try:
                handler = ExcelHandler(archivo, tipo_carga, request.user, mercado)
                carga = handler.procesar()

                messages.success(request, f"Carga procesada correctamente (ID {carga.id}).")
                return redirect("accounts:detalle_carga", pk=carga.id)

            except Exception as e:
                messages.error(request, f"Error procesando carga: {str(e)}")

    else:
        form = CargaMasivaForm()

    return render(request, "accounts/nueva_carga.html", {"form": form})


@login_required
def detalle_carga(request, pk):
    from api.models import CargaMasiva

    carga = get_object_or_404(CargaMasiva, pk=pk, iniciado_por=request.user)
    calificaciones = CalificacionTributaria.objects.filter(carga=carga)

    return render(request, "accounts/detalle_carga.html", {"carga": carga, "calificaciones": calificaciones})


@login_required
def descargar_plantilla(request):
    archivo = generar_plantilla_excel()
    response = HttpResponse(
        archivo,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=plantilla_carga.xlsx"
    return response


# ===============================
# Calificaciones
# ===============================
@login_required
def lista_calificaciones(request):
    calificaciones = CalificacionTributaria.objects.filter(usuario=request.user)
    return render(request, "accounts/lista_calificaciones.html", {"calificaciones": calificaciones})


@login_required
def detalle_calificacion(request, pk):
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk, usuario=request.user)
    return render(request, "accounts/detalle_calificacion.html", {"calificacion": calificacion})


@login_required
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk, usuario=request.user)

    class CalificacionForm(ModelForm):
        class Meta:
            model = CalificacionTributaria
            fields = "__all__"

    if request.method == "POST":
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            messages.success(request, "Calificación actualizada correctamente.")
            return redirect("accounts:lista_calificaciones")
    else:
        form = CalificacionForm(instance=calificacion)

    return render(request, "accounts/editar_calificacion.html", {"form": form, "calificacion": calificacion})


@login_required
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk, usuario=request.user)

    if request.method == "POST":
        calificacion.delete()
        messages.success(request, "Calificación eliminada correctamente.")
        return redirect("accounts:lista_calificaciones")

    return render(request, "accounts/eliminar_calificacion.html", {"calificacion": calificacion})


@login_required
def lista_logs(request):
    # Por ahora muestra un mensaje simple
    logs = []  # Aquí podrías traer tus logs reales más adelante
    return render(request, "accounts/lista_logs.html", {"logs": logs})
