# api/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import Perfil
from api.models import CalificacionTributaria, CargaMasiva, LogOperacion
from api.serializers import (
    CalificacionTributariaListSerializer,
    CargaMasivaSerializer,
    LogOperacionSerializer,
    RegistroSerializer,
    PerfilSerializer,
)
from api.services import (
    registrar_log,
    obtener_estadisticas_dashboard,
    calificaciones_por_agrupacion,
    estadisticas_cargas,
)


# -------------------------------
# ViewSets
# -------------------------------

class PerfilViewSet(viewsets.ModelViewSet):
    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Perfil.objects.all() 


class CalificacionTributariaViewSet(viewsets.ModelViewSet):
    serializer_class = CalificacionTributariaListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CalificacionTributaria.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        obj = serializer.save(usuario=self.request.user)
        registrar_log(self.request.user, "CREATE", obj)

    def perform_update(self, serializer):
        instance = self.get_object()
        antes = serializer.to_representation(instance)
        obj = serializer.save()
        despues = serializer.to_representation(obj)
        registrar_log(self.request.user, "UPDATE", obj, antes, despues)

    def perform_destroy(self, instance):
        registrar_log(self.request.user, "DELETE", instance)
        instance.delete()


class CargaMasivaViewSet(viewsets.ModelViewSet):
    serializer_class = CargaMasivaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CargaMasiva.objects.filter(iniciado_por=self.request.user)

    def perform_create(self, serializer):
        obj = serializer.save(iniciado_por=self.request.user)
        registrar_log(self.request.user, "CREATE", None, datos_nuevos={"carga_id": obj.id})


class LogOperacionViewSet(viewsets.ModelViewSet):
    serializer_class = LogOperacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LogOperacion.objects.filter(usuario=self.request.user)


# -------------------------------
# API Views
# -------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    return Response(obtener_estadisticas_dashboard(request.user))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def calificaciones_por_mercado(request):
    data = calificaciones_por_agrupacion(
        CalificacionTributaria.objects.filter(usuario=request.user),
        "mercado"
    )
    return Response(list(data))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def calificaciones_por_divisa(request):
    data = calificaciones_por_agrupacion(
        CalificacionTributaria.objects.filter(usuario=request.user),
        "divisa"
    )
    return Response(list(data))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cargas_estadisticas(request):
    data = estadisticas_cargas(CargaMasiva.objects.filter(iniciado_por=request.user))
    return Response(data)


@api_view(["POST"])
def registro_api(request):
    serializer = RegistroSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})
