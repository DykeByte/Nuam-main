# api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import (
    CalificacionTributaria, 
    CargaMasiva, 
    LogOperacion,
    Calificacion,
    Divisa,
    LogAuditoria
)
from accounts.models import Perfil


# ========================
# User Serializers
# ========================
class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para el modelo User"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserDetailSerializer(UserSerializer):
    """Serializer detallado con perfil"""
    perfil = serializers.SerializerMethodField()
    total_calificaciones = serializers.SerializerMethodField()
    total_cargas = serializers.SerializerMethodField()
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['perfil', 'total_calificaciones', 'total_cargas']
    
    def get_perfil(self, obj):
        try:
            return PerfilSerializer(obj.perfil).data
        except:
            return None
    
    def get_total_calificaciones(self, obj):
        return obj.calificaciones_tributarias.count()
    
    def get_total_cargas(self, obj):
        return obj.cargas_masivas.count()


class PerfilSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Perfil
        fields = '__all__'
        read_only_fields = ['usuario']


class RegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, min_length=8)
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe")
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


# ========================
# Calificación Tributaria Serializers
# ========================
class CalificacionTributariaSerializer(serializers.ModelSerializer):
    """Serializer completo para CalificacionTributaria"""
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    carga_nombre = serializers.CharField(source='carga_masiva.archivo_nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = CalificacionTributaria
        fields = '__all__'
        read_only_fields = ['usuario', 'created_at', 'updated_at']


class CalificacionTributariaListSerializer(serializers.ModelSerializer):
    """Versión simplificada para listados"""
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = CalificacionTributaria
        fields = [
            'id', 'corredor_dueno', 'instrumento', 'mercado', 'divisa',
            'valor_historico', 'fecha_pago', 'usuario_nombre', 'created_at', 'es_local'
        ]


class CalificacionTributariaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear calificaciones manualmente"""
    
    class Meta:
        model = CalificacionTributaria
        exclude = ['usuario', 'carga_masiva', 'created_at', 'updated_at']


# ========================
# Carga Masiva Serializers
# ========================
class CargaMasivaSerializer(serializers.ModelSerializer):
    """Serializer para CargaMasiva"""
    iniciado_por_nombre = serializers.CharField(source='iniciado_por.username', read_only=True)
    porcentaje_exito = serializers.SerializerMethodField()
    
    class Meta:
        model = CargaMasiva
        fields = '__all__'
        read_only_fields = ['iniciado_por', 'fecha_inicio', 'registros_procesados', 
                           'registros_exitosos', 'registros_fallidos', 'estado']
    
    def get_porcentaje_exito(self, obj):
        if obj.registros_procesados == 0:
            return 0
        return round((obj.registros_exitosos / obj.registros_procesados) * 100, 2)


class CargaMasivaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado con calificaciones asociadas"""
    iniciado_por_nombre = serializers.CharField(source='iniciado_por.username', read_only=True)
    porcentaje_exito = serializers.SerializerMethodField()
    calificaciones = CalificacionTributariaListSerializer(
        source='calificaciones_tributarias', 
        many=True, 
        read_only=True
    )
    total_calificaciones = serializers.SerializerMethodField()
    
    class Meta:
        model = CargaMasiva
        fields = '__all__'  # Incluye todos los campos del modelo
    
    def get_porcentaje_exito(self, obj):
        if obj.registros_procesados == 0:
            return 0
        return round((obj.registros_exitosos / obj.registros_procesados) * 100, 2)
    
    def get_total_calificaciones(self, obj):
        return obj.calificaciones_tributarias.count()


# ========================
# Log Serializers
# ========================
class LogOperacionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    calificacion_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = LogOperacion
        fields = '__all__'
        read_only_fields = ['fecha_hora']
    
    def get_calificacion_detalle(self, obj):
        if obj.calificacion:
            return {
                'id': obj.calificacion.id,
                'instrumento': obj.calificacion.instrumento,
                'corredor': obj.calificacion.corredor_dueno
            }
        return None


class LogAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = LogAuditoria
        fields = '__all__'
        read_only_fields = ['timestamp']


# ========================
# Calificación General Serializers
# ========================
class CalificacionSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(source='creado_por.username', read_only=True)
    
    class Meta:
        model = Calificacion
        fields = '__all__'
        read_only_fields = ['creado_por', 'creado_en', 'actualizado_en']


# ========================
# Divisa Serializers
# ========================
class DivisaSerializer(serializers.ModelSerializer):
    """Serializer para divisas"""
    
    class Meta:
        model = Divisa
        fields = '__all__'
        read_only_fields = ['fecha_actualizacion']


# ========================
# Estadísticas Serializers
# ========================
class EstadisticasSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    total_calificaciones = serializers.IntegerField()
    total_cargas = serializers.IntegerField()
    cargas_exitosas = serializers.IntegerField()
    cargas_con_errores = serializers.IntegerField()
    tasa_exito = serializers.FloatField()
    por_mercado = serializers.DictField()
    por_divisa = serializers.DictField()
    por_tipo_carga = serializers.DictField()
    ultimas_cargas = CargaMasivaSerializer(many=True)


class CargaMasivaUploadSerializer(serializers.Serializer):
    """Serializer para carga de archivos"""
    archivo = serializers.FileField()
    tipo_carga = serializers.ChoiceField(choices=['FACTORES', 'MONITOR'])
    mercado = serializers.ChoiceField(choices=['LOCAL', 'INTERNACIONAL'])
    
    def validate_archivo(self, value):
        # Validar tamaño (5MB máximo)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("El archivo no debe superar 5MB")
        
        # Validar extensión
        nombre = value.name.lower()
        if not (nombre.endswith('.xlsx') or nombre.endswith('.xls') or nombre.endswith('.csv')):
            raise serializers.ValidationError("Solo se aceptan archivos .xlsx, .xls o .csv")
        
        return value