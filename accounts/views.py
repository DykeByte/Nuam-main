from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm

#from api import procesar_carga_masiva, generar_plantilla_excel
from api.forms import CargaMasivaForm
from api.models import CalificacionTributaria
import logging

logger = logging.getLogger(__name__)

# ===============================
# Vistas de Autenticación Web
# ===============================
def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"✅ Nuevo usuario registrado: {user.username}")
            messages.success(request, "Cuenta creada correctamente. Ya puedes iniciar sesión.")
            return redirect("accounts:login")
        else:
            logger.warning(f"❌ Intento de registro fallido. Errores: {form.errors}")
    else:
        form = UserCreationForm()
    return render(request, "accounts/registro.html", {"form": form})


def mi_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"✅ Login exitoso - Usuario: {user.username} | IP: {request.META.get('REMOTE_ADDR')}")
            return redirect("accounts:home")
        else:
            username = request.POST.get('username', 'desconocido')
            logger.warning(f"❌ Login fallido - Usuario: {username} | IP: {request.META.get('REMOTE_ADDR')}")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


@login_required
def mi_logout(request):
    username = request.user.username
    logout(request)
    logger.info(f"🚪 Logout - Usuario: {username}")
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("accounts:login")


# ===============================
# Dashboard / Home
# ===============================
@login_required
def home(request):
    logger.debug(f"🏠 Acceso a home - Usuario: {request.user.username}")
    return render(request, "home.html")


# ===============================
# Cargas Masivas
# ===============================
@login_required
def lista_cargas(request):
    """Lista todas las cargas masivas del usuario"""
    from api.models import CargaMasiva
    
    logger.info(f"📋 Lista de cargas - Usuario: {request.user.username}")
    
    try:
        cargas = CargaMasiva.objects.filter(iniciado_por=request.user).order_by('-fecha_inicio')
        logger.debug(f"   Total de cargas: {cargas.count()}")
        
        return render(request, "accounts/lista_cargas.html", {"cargas": cargas})
        
    except Exception as e:
        logger.error(f"❌ Error listando cargas: {str(e)}", exc_info=True)
        messages.error(request, f"Error al cargar la lista: {str(e)}")
        return render(request, "accounts/lista_cargas.html", {"cargas": []})


@login_required
def nueva_carga(request):
    from api.excel_handler import ExcelHandler 
    
    logger.info(f"{'='*60}")
    logger.info(f"🔵 INICIO nueva_carga() - Usuario: {request.user.username}")
    logger.info(f"   Método: {request.method}")

    if request.method == "POST":
        logger.info(f"📤 POST detectado")
        logger.info(f"   FILES recibidos: {list(request.FILES.keys())}")
        logger.info(f"   POST data keys: {list(request.POST.keys())}")
        
        form = CargaMasivaForm(request.POST, request.FILES)
        
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            tipo_carga = form.cleaned_data["tipo_carga"]
            mercado = form.cleaned_data["mercado"]
            
            logger.info(f"✅ Formulario válido")
            logger.info(f"   - Archivo: {archivo.name}")
            logger.info(f"   - Tamaño: {archivo.size} bytes ({archivo.size/1024:.2f} KB)")
            logger.info(f"   - Content-Type: {archivo.content_type}")
            logger.info(f"   - Tipo de carga: {tipo_carga}")
            logger.info(f"   - Mercado: {mercado}")

            try:
                logger.info(f"🔄 Iniciando procesamiento con ExcelHandler...")
                handler = ExcelHandler(archivo, tipo_carga, request.user)
                handler.mercado = mercado  # ← Asignar mercado
                
                logger.info(f"🔄 Ejecutando handler.procesar()...")
                carga = handler.procesar()
                
                logger.info(f"✅ ¡CARGA EXITOSA! ID: {carga.id}")
                logger.info(f"   - Estado: {carga.estado}")
                logger.info(f"   - Registros procesados: {carga.registros_procesados}")
                logger.info(f"   - Registros exitosos: {carga.registros_exitosos}")
                logger.info(f"   - Registros fallidos: {carga.registros_fallidos}")
                
                messages.success(request, f"Carga procesada correctamente (ID {carga.id}). Exitosos: {carga.registros_exitosos}, Fallidos: {carga.registros_fallidos}")
                return redirect("accounts:detalle_carga", pk=carga.id)

            except Exception as e:
                logger.error(f"❌ ERROR CRÍTICO en procesamiento")
                logger.error(f"   Tipo de error: {type(e).__name__}")
                logger.error(f"   Mensaje: {str(e)}")
                logger.error(f"   Traceback completo:", exc_info=True)
                
                messages.error(request, f"Error procesando carga: {str(e)}")
        else:
            logger.error(f"❌ Formulario INVÁLIDO")
            logger.error(f"   Errores: {form.errors}")
            logger.error(f"   Errores no de campo: {form.non_field_errors()}")
            
            messages.error(request, f"Formulario inválido: {form.errors}")

    else:
        form = CargaMasivaForm()
        logger.info(f"📋 Mostrando formulario vacío")

    logger.info(f"{'='*60}")
    return render(request, "accounts/nueva_carga.html", {"form": form})

@login_required
def detalle_carga(request, pk):
    from api.models import CargaMasiva
    
    logger.info(f"👁️ Accediendo a detalle_carga - ID: {pk} - Usuario: {request.user.username}")
    
    try:
        carga = get_object_or_404(CargaMasiva, pk=pk, iniciado_por=request.user)
        
        # CAMBIO AQUÍ: carga_masiva en vez de carga
        calificaciones = CalificacionTributaria.objects.filter(carga_masiva=carga)
        
        logger.info(f"✅ Carga encontrada: {carga}")
        logger.info(f"   Calificaciones asociadas: {calificaciones.count()}")
        
        return render(request, "accounts/detalle_carga.html", {
            "carga": carga, 
            "calificaciones": calificaciones
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo detalle de carga {pk}: {str(e)}", exc_info=True)
        raise


@login_required
def descargar_plantilla(request):
    logger.info(f"📥 Descarga de plantilla - Usuario: {request.user.username}")
    
    try:
        archivo = generar_plantilla_excel()
        response = HttpResponse(
            archivo,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=plantilla_carga.xlsx"
        logger.info(f"✅ Plantilla generada correctamente")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generando plantilla: {str(e)}", exc_info=True)
        messages.error(request, f"Error al generar plantilla: {str(e)}")
        return redirect("accounts:nueva_carga")


# ===============================
# Calificaciones
# ===============================
@login_required
def lista_calificaciones(request):
    logger.debug(f"📋 Listando calificaciones - Usuario: {request.user.username}")
    calificaciones = CalificacionTributaria.objects.filter(usuario=request.user)
    logger.debug(f"   Total encontradas: {calificaciones.count()}")
    return render(request, "accounts/lista_calificaciones.html", {"calificaciones": calificaciones})


@login_required
def detalle_calificacion(request, pk):
    logger.debug(f"👁️ Detalle calificación {pk} - Usuario: {request.user.username}")
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
            logger.info(f"✏️ Calificación {pk} actualizada por {request.user.username}")
            messages.success(request, "Calificación actualizada correctamente.")
            return redirect("accounts:lista_calificaciones")
        else:
            logger.warning(f"❌ Error actualizando calificación {pk}: {form.errors}")
    else:
        form = CalificacionForm(instance=calificacion)

    return render(request, "accounts/editar_calificacion.html", {"form": form, "calificacion": calificacion})


@login_required
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk, usuario=request.user)

    if request.method == "POST":
        calificacion.delete()
        logger.info(f"🗑️ Calificación {pk} eliminada por {request.user.username}")
        messages.success(request, "Calificación eliminada correctamente.")
        return redirect("accounts:lista_calificaciones")

    return render(request, "accounts/eliminar_calificacion.html", {"calificacion": calificacion})


# ===============================
# Logs del Sistema
# ===============================
@login_required
def lista_logs(request):
    """Muestra los logs de operaciones del usuario"""
    from api.models import LogOperacion
    
    logger.debug(f"📋 Lista de logs - Usuario: {request.user.username}")
    
    try:
        logs = LogOperacion.objects.filter(usuario=request.user).order_by('-fecha_hora')[:100]
        logger.debug(f"   Total de logs: {logs.count()}")
        
        return render(request, "accounts/lista_logs.html", {"logs": logs})
        
    except Exception as e:
        logger.error(f"❌ Error listando logs: {str(e)}", exc_info=True)
        return render(request, "accounts/lista_logs.html", {"logs": []})