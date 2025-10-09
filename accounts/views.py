# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Perfil, CargaMasiva, CalificacionTributaria, LogOperacion
from .utils.divisas import obtener_tipo_cambio
from forex_python.converter import CurrencyRates



# ==================== AUTENTICACIÓN ====================

def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'accounts/registro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'accounts/registro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return render(request, 'accounts/registro.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Cuenta creada. Esperando aprobación del administrador.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/registro.html')


def mi_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Permite login si es superuser o si el perfil está aprobado
            if user.is_superuser or user.perfil.aprobado:
                login(request, user)
                messages.success(request, f'Bienvenido {user.username}')
                return redirect('accounts:home')
            else:
                messages.error(request, 'Tu cuenta aún no ha sido aprobada por el administrador')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'accounts/login.html')


@login_required
def mi_logout(request):
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('accounts:login')


# ==================== HOME/DASHBOARD ====================

@login_required
@login_required
def home(request):
    # Permite acceso si es superuser o si el perfil está aprobado
    if not request.user.is_superuser and not request.user.perfil.aprobado:
        messages.warning(request, 'Tu cuenta está pendiente de aprobación')
        return redirect('accounts:login')
    
    # Estadísticas para el dashboard
    total_calificaciones = CalificacionTributaria.objects.filter(usuario=request.user).count()
    total_cargas = CargaMasiva.objects.filter(usuario=request.user).count()
    ultimas_cargas = CargaMasiva.objects.filter(usuario=request.user)[:5]
    
    context = {
        'total_calificaciones': total_calificaciones,
        'total_cargas': total_cargas,
        'ultimas_cargas': ultimas_cargas,
    }
    return render(request, 'home.html', context)


# ==================== CARGAS MASIVAS ====================

@login_required
def lista_cargas(request):
    cargas = CargaMasiva.objects.filter(usuario=request.user)
    return render(request, 'accounts/lista_cargas.html', {'cargas': cargas})


@login_required
def nueva_carga(request):
    # Diccionario de divisas para pruebas
    tasas_divisas = {
        'USD': 850,   # 1 USD = 850 CLP
        'EUR': 920,   # 1 EUR = 920 CLP
        'CAD': 650,   # 1 CAD = 650 CLP
        'COL': 0.22,  # 1 COP = 0.22 CLP
        'PEN': 210,   # 1 PEN = 210 CLP
        'CLP': 1,     # Peso chileno como referencia
    }

    if request.method == 'POST':
        # Aquí lógica de carga de archivos
        messages.info(request, 'Funcionalidad de carga en desarrollo')
        return redirect('accounts:lista_cargas')
    
    context = {
        'tasas_divisas': tasas_divisas
    }
    return render(request, 'accounts/nueva_carga.html', context)



@login_required
def detalle_carga(request, pk):
    carga = get_object_or_404(CargaMasiva, pk=pk, usuario=request.user)
    calificaciones = CalificacionTributaria.objects.filter(carga_masiva=carga)
    
    context = {
        'carga': carga,
        'calificaciones': calificaciones,
    }
    return render(request, 'accounts/detalle_carga.html', context)


# ==================== CALIFICACIONES ====================

@login_required
def lista_calificaciones(request):
    calificaciones = CalificacionTributaria.objects.filter(usuario=request.user)
    return render(request, 'accounts/lista_calificaciones.html', {'calificaciones': calificaciones})


@login_required
def detalle_calificacion(request, pk):
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk, usuario=request.user)
    return render(request, 'accounts/detalle_calificacion.html', {'calificacion': calificacion})


@login_required
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        # Guardar datos anteriores para el log
        datos_anteriores = {
            'corredor_dueno': calificacion.corredor_dueno,
            'mercado': calificacion.mercado,
            'instrumento': calificacion.instrumento,
        }
        
        # Actualizar campos
        calificacion.corredor_dueno = request.POST.get('corredor_dueno', '')
        calificacion.mercado = request.POST.get('mercado', '')
        calificacion.instrumento = request.POST.get('instrumento', '')
        calificacion.save()
        
        # Crear log
        LogOperacion.objects.create(
            usuario=request.user,
            calificacion=calificacion,
            operacion='UPDATE',
            datos_anteriores=datos_anteriores,
            datos_nuevos={
                'corredor_dueno': calificacion.corredor_dueno,
                'mercado': calificacion.mercado,
                'instrumento': calificacion.instrumento,
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Calificación actualizada exitosamente')
        return redirect('accounts:detalle_calificacion', pk=pk)
    
    return render(request, 'accounts/editar_calificacion.html', {'calificacion': calificacion})


@login_required
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        # Crear log antes de eliminar
        LogOperacion.objects.create(
            usuario=request.user,
            operacion='DELETE',
            datos_anteriores={'id': calificacion.id, 'instrumento': calificacion.instrumento},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        calificacion.delete()
        messages.success(request, 'Calificación eliminada exitosamente')
        return redirect('accounts:lista_calificaciones')
    
    return render(request, 'accounts/eliminar_calificacion.html', {'calificacion': calificacion})


# ==================== LOGS ====================

@login_required
def lista_logs(request):
    logs = LogOperacion.objects.filter(usuario=request.user)
    return render(request, 'accounts/lista_logs.html', {'logs': logs})