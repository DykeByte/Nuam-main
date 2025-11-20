# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from accounts.models import Perfil
import re
import logging

from api.forms import CargaMasivaForm
from api.models import CalificacionTributaria

logger = logging.getLogger(__name__)


# ===============================
# Vista de Registro CORREGIDA
# ===============================
def registro(request):
    """Vista de registro con validación completa"""
    
    if request.method == "POST":
        # Obtener datos del formulario
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
        logger.info(f"📝 Intento de registro - Username: {username}, Email: {email}")
        
        # Lista de errores
        errors = []
        
        # ============ VALIDACIONES ============
        
        # 1. Validar username
        if not username:
            errors.append("El nombre de usuario es obligatorio")
        elif len(username) < 3:
            errors.append("El nombre de usuario debe tener al menos 3 caracteres")
        elif not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
            errors.append("El nombre de usuario debe comenzar con letra y solo contener letras, números y guiones bajos")
        elif User.objects.filter(username=username).exists():
            errors.append("Este nombre de usuario ya está en uso")
        
        # 2. Validar email
        if not email:
            errors.append("El correo electrónico es obligatorio")
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("Ingresa un correo electrónico válido")
        elif User.objects.filter(email=email).exists():
            errors.append("Este correo electrónico ya está registrado")
        
        # 3. Validar contraseña
        if not password:
            errors.append("La contraseña es obligatoria")
        elif len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres")
        elif not re.search(r'[A-Z]', password):
            errors.append("La contraseña debe contener al menos una letra mayúscula")
        elif not re.search(r'[a-z]', password):
            errors.append("La contraseña debe contener al menos una letra minúscula")
        elif not re.search(r'\d', password):
            errors.append("La contraseña debe contener al menos un número")
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("La contraseña debe contener al menos un carácter especial")
        
        # 4. Validar confirmación
        if password != password2:
            errors.append("Las contraseñas no coinciden")
        
        # ============ SI HAY ERRORES ============
        if errors:
            logger.warning(f"❌ Registro fallido - Errores: {errors}")
            for error in errors:
                messages.error(request, error)
            return render(request, "accounts/registro.html")
        
        # ============ CREAR USUARIO ============
        try:
            # Crear el usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            logger.info(f"✅ Usuario creado en BD: {user.username} (ID: {user.id})")
            
            # Verificar que se creó el perfil automáticamente
            try:
                perfil = user.perfil
                logger.info(f"✅ Perfil creado automáticamente: ID={perfil.id}, aprobado={perfil.aprobado}")
            except Perfil.DoesNotExist:
                # Si no existe, crearlo manualmente
                logger.warning(f"⚠️ Perfil no creado automáticamente - Creando manualmente...")
                perfil = Perfil.objects.create(user=user, aprobado=False)
                logger.info(f"✅ Perfil creado manualmente: ID={perfil.id}")
            
            messages.success(
                request,
                "¡Cuenta creada correctamente! Tu cuenta será revisada por un administrador antes de ser activada."
            )
            logger.info(f"✅ Registro completado exitosamente para: {username}")
            
            return redirect("accounts:login")
            
        except Exception as e:
            logger.error(f"❌ ERROR al crear usuario: {str(e)}", exc_info=True)
            messages.error(request, f"Error al crear la cuenta. Por favor, intenta de nuevo.")
            return render(request, "accounts/registro.html")
    
    else:
        # GET - Mostrar formulario vacío
        logger.debug("📄 Mostrando formulario de registro (GET)")
        return render(request, "accounts/registro.html")


# ===============================
# Vistas de Autenticación Web
# ===============================
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
                handler.mercado = mercado
                
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
    from api import generar_plantilla_excel
    
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