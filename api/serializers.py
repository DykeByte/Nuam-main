#api/serializers.py 

from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Calificacion, CalificacionTributaria, CargaMasiva, LogOperacion, LogAuditoria, Divisa
from accounts.models import Perfil

class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class PerfilSerializer(serializers.ModelSerializer):
    """Serializer para Perfil de usuario"""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Perfil
        fields = ['user', 'username', 'email', 'rut', 'nombre_completo', 'aprobado']
        read_only_fields = ['aprobado']


class CalificacionTributariaSerializer(serializers.ModelSerializer):
    """Serializer para CalificacionTributaria con todos los campos"""
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    carga_masiva_nombre = serializers.CharField(source='carga_masiva.nombre_archivo', read_only=True, allow_null=True)
    
    # Campos calculados
    url = serializers.HyperlinkedIdentityField(view_name='api:calificacion-detail')
    
    class Meta:
        model = CalificacionTributaria
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'created_at', 'updated_at', 'usuario_nombre', 'carga_masiva_nombre', 'url']
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar que los factores estén en rango válido si se proporcionan
        for i in range(8, 38):
            factor_name = f'factor_{i}'
            factor_value = data.get(factor_name)
            if factor_value is not None and (factor_value < 0 or factor_value > 10):
                raise serializers.ValidationError({
                    factor_name: f"El {factor_name} debe estar entre 0 y 10"
                })
        
        return data


class CalificacionTributariaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados (sin todos los factores)"""
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='api:calificacion-detail')
    
    class Meta:
        model = CalificacionTributaria
        fields = [
            'id', 'url', 'usuario_nombre', 'corredor_dueno', 'rut_es_el_manual',
            'ano_comercial', 'mercado', 'instrumento', 'fecha_pago',
            'valor_historico', 'divisa', 'created_at', 'updated_at'
        ]


class CargaMasivaSerializer(serializers.ModelSerializer):
    """Serializer para CargaMasiva"""
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    calificaciones_count = serializers.SerializerMethodField()
    tasa_exito = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(view_name='api:carga-detail')
    
    class Meta:
        model = CargaMasiva
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'fecha_carga', 'usuario_nombre', 'url']
    
    def get_calificaciones_count(self, obj):
        """Retorna el número de calificaciones asociadas"""
        return obj.calificaciontributaria_set.count()
    
    def get_tasa_exito(self, obj):
        """Calcula la tasa de éxito en porcentaje"""
        if obj.registros_procesados > 0:
            return round((obj.registros_exitosos / obj.registros_procesados) * 100, 2)
        return 0


class LogOperacionSerializer(serializers.ModelSerializer):
    """Serializer para LogOperacion"""
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    operacion_display = serializers.CharField(source='get_operacion_display', read_only=True)
    
    class Meta:
        model = LogOperacion
        fields = '__all__'
        read_only_fields = ['id', 'fecha_hora', 'usuario_nombre']


class RegistroSerializer(serializers.Serializer):
    """Serializer para registro de nuevos usuarios via API"""
    username = serializers.CharField(max_length=150, min_length=3)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    nombre_completo = serializers.CharField(max_length=255, required=False, allow_blank=True)
    rut = serializers.CharField(max_length=12, required=False, allow_blank=True)
    
    def validate_username(self, value):
        """Validar username"""
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', value):
            raise serializers.ValidationError(
                "El username debe comenzar con letra y solo contener letras, números y guiones bajos"
            )
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este username ya existe")
        return value
    
    def validate_email(self, value):
        """Validar email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado")
        return value.lower()
    
    def validate(self, data):
        """Validar que las contraseñas coincidan"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Las contraseñas no coinciden"})
        return data
    
    def create(self, validated_data):
        """Crear usuario y perfil"""
        validated_data.pop('password2')
        nombre_completo = validated_data.pop('nombre_completo', '')
        rut = validated_data.pop('rut', '')
        
        user = User.objects.create_user(**validated_data)
        
        # Actualizar perfil
        user.perfil.nombre_completo = nombre_completo
        user.perfil.rut = rut
        user.perfil.save()
        
        return user


class EstadisticasSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    total_calificaciones = serializers.IntegerField()
    total_cargas = serializers.IntegerField()
    cargas_ultimo_mes = serializers.IntegerField()
    calificaciones_por_mercado = serializers.DictField()
    ultimas_cargas = CargaMasivaSerializer(many=True)