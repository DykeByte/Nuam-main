# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Perfil, CargaMasiva, CalificacionTributaria, LogOperacion
from forex_python.converter import CurrencyRates
from .excel_handler import ExcelHandler, get_columnas_esperadas
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from .forms import RegistroForm



# ==================== AUTENTICACIÓN ====================

def registro(request):
    """Vista de registro con validaciones robustas"""
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        
        if form.is_valid():
            try:
                # Crear usuario
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                
                # El perfil se crea automáticamente por el signal
                
                messages.success(
                    request, 
                    '¡Cuenta creada exitosamente! Tu cuenta está pendiente de aprobación por el administrador.'
                )
                return redirect('accounts:login')
                
            except Exception as e:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')
        
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    
    else:
        form = RegistroForm()
    
    return render(request, 'accounts/registro.html', {'form': form})


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
    tasas = ['CLP', 'PEN', 'COP']  # Monedas disponibles

    if request.method == 'POST':
        tipo_carga = request.POST.get('tipo_carga')
        archivo = request.FILES.get('archivo')
        mercado_seleccionado = request.POST.get('mercado', 'CLP')  # default CLP

        # Validaciones básicas
        if not tipo_carga or not archivo:
            messages.error(request, 'Debes completar todos los campos')
            context = {
                'columnas_factores': get_columnas_esperadas('FACTORES'),
                'columnas_monitor': get_columnas_esperadas('MONITOR'),
                'tasas': tasas,
                'mercado_seleccionado': mercado_seleccionado
            }
            return render(request, 'accounts/nueva_carga.html', context)

        # Validar extensión y tamaño
        if not archivo.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Solo se permiten archivos Excel (.xlsx, .xls)')
            return render(request, 'accounts/nueva_carga.html', context)
        if archivo.size > 5 * 1024 * 1024:
            messages.error(request, 'El archivo es muy grande. Máximo 5MB')
            return render(request, 'accounts/nueva_carga.html', context)

        try:
            # Procesar el archivo
            handler = ExcelHandler(archivo, tipo_carga, request.user)
            carga = handler.procesar()

            # Conversión de moneda
            cr = CurrencyRates()
            factor_conversion = 1.0
            if mercado_seleccionado != 'CLP':
                factor_conversion = cr.get_rate('CLP', mercado_seleccionado)

            # Aplicar la conversión a todos los registros de la carga
            for calificacion in carga.calificaciontributaria_set.all():
                if calificacion.valor_historico:
                    calificacion.valor_convertido = calificacion.valor_historico * factor_conversion
                    calificacion.moneda = mercado_seleccionado
                    calificacion.save()

            # Mensaje de éxito
            if carga.registros_fallidos > 0:
                messages.warning(
                    request,
                    f'Carga completada con advertencias: {carga.registros_exitosos} exitosos, {carga.registros_fallidos} fallidos. Valores convertidos a {mercado_seleccionado}.'
                )
            else:
                messages.success(
                    request,
                    f'¡Carga exitosa! {carga.registros_exitosos} registros procesados. Valores convertidos a {mercado_seleccionado}.'
                )

            return redirect('accounts:detalle_carga', pk=carga.pk)

        except Exception as e:
            messages.error(request, f'Error al procesar archivo: {str(e)}')
            return render(request, 'accounts/nueva_carga.html', context={'tasas': tasas, 'mercado_seleccionado': 'CLP'})

    # GET request
    context = {
        'columnas_factores': get_columnas_esperadas('FACTORES'),
        'columnas_monitor': get_columnas_esperadas('MONITOR'),
        'tasas': tasas,
        'mercado_seleccionado': 'CLP'
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

@login_required
def descargar_plantilla(request):
    """Genera y descarga una plantilla Excel actualizada con los campos reales del modelo"""
    
    # Datos de ejemplo sincronizados con el modelo real
    datos = {
        # Campos básicos
        'corredor_dueno': ['Corredor Ejemplo A', 'Corredor Ejemplo B'],
        'rut_es_el_manual': ['12345678-9', '98765432-1'],
        'ano_comercial': ['2024', '2024'],
        'mercado': ['ACN', 'OCT'],
        'instrumento': ['BONO-001', 'BONO-002'],
        'fecha_pago': ['2024-12-31', '2024-11-30'],
        'secuencia_evento': [1, 2],
        'numero_dividendo': [1, 1],
        'descripcion': ['Descripción ejemplo 1', 'Descripción ejemplo 2'],
        'tipo_sociedad': ['A/C', 'A/C'],
        'divisa': ['CLP', 'USD'],
        'acopio_lsfxf': ['true', 'false'],
        'valor_historico': [1000000.00, 2000000.00],
        'factor_actualizacion': [1.05, 1.03],
        'valor_convertido': [1050000.00, 2060000.00],
        'origen': ['CARGA_MASIVA', 'CARGA_MASIVA'],
        'es_local': ['true', 'true'],
    }
    
    # Agregar factores del 8 al 37 (30 factores)
    for i in range(8, 38):
        datos[f'factor_{i}'] = [1.0 + (i/100), 1.0 + (i/100)]
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
        
        # Obtener el workbook y worksheet para dar formato
        workbook = writer.book
        worksheet = writer.sheets['Datos']
        
        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    # Crear respuesta HTTP
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=plantilla_carga_nuam.xlsx'
    
    return response

def get_columnas_esperadas(tipo_carga):
    """
    Devuelve las columnas esperadas según el tipo de carga masiva.
    """
    if tipo_carga == 'FACTORES':
        return [
            'corredor_dueno',
            'rut',
            'ano_comercial',
            'mercado',
            'instrumento',
            'fecha_pago',
            'secuencia_evento',
            'numero_dividendo',
            'descripcion',
            'tipo_sociedad',
            'acopio_lsfxf',
            'valor_historico',
            'factor_actualizacion',
            'es_local',
            'origen'
        ]
    
    elif tipo_carga == 'MONITOR':
        return [
            'fecha',
            'indicador',
            'valor',
            'fuente',
            'observaciones'
        ]
    
    else:
        return []

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