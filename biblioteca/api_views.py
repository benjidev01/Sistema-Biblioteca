from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Libro, Prestamo, Socio
from .serializers import LibroSerializer, PrestamoSerializer, SocioSerializer


def is_admin(user):
    return bool(user and user.is_authenticated and (
        user.is_staff
        or user.is_superuser
        or user.groups.filter(name__in=('Administrador', 'Administradores')).exists()
    ))


def error_response(message, code=status.HTTP_400_BAD_REQUEST, details=None):
    payload = {'detail': message}
    if details:
        payload['errors'] = details
    return Response(payload, status=code)


def serialize_error(serializer):
    return error_response('Los datos enviados no son válidos.', details=serializer.errors)


@extend_schema(
    methods=['GET', 'POST'],
    summary='Listar o crear socios',
    description='Los campos privados de un socio solo se muestran a administradores.',
    request=SocioSerializer,
    responses={200: SocioSerializer(many=True), 201: SocioSerializer, 400: OpenApiResponse(description='Datos inválidos')},
    examples=[OpenApiExample('Socio', value={'rut': '12345678-5', 'nombre': 'Ana Pérez', 'email': 'ana@example.com', 'telefono': '+56 912345678'})],
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def socio_list_create(request):
    if request.method == 'GET':
        serializer = SocioSerializer(Socio.objects.all(), many=True, context={'request': request})
        return Response(serializer.data)
    if not is_admin(request.user):
        return error_response('Solo un administrador puede crear socios.', status.HTTP_403_FORBIDDEN)
    serializer = SocioSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return serialize_error(serializer)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    methods=['GET', 'PUT', 'DELETE'],
    summary='Consultar, actualizar o eliminar un socio',
    request=SocioSerializer,
    responses={200: SocioSerializer, 400: OpenApiResponse(description='Datos inválidos'), 404: OpenApiResponse(description='No encontrado')},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def socio_detail(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'GET':
        return Response(SocioSerializer(socio, context={'request': request}).data)
    if not is_admin(request.user):
        return error_response('Solo un administrador puede modificar socios.', status.HTTP_403_FORBIDDEN)
    if request.method == 'DELETE':
        socio.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = SocioSerializer(socio, data=request.data, context={'request': request})
    if not serializer.is_valid():
        return serialize_error(serializer)
    serializer.save()
    return Response(serializer.data)


@extend_schema(
    methods=['GET', 'POST'],
    summary='Listar o crear libros',
    request=LibroSerializer,
    responses={200: LibroSerializer(many=True), 201: LibroSerializer, 400: OpenApiResponse(description='Datos inválidos')},
    examples=[OpenApiExample('Libro', value={'titulo': 'Clean Code', 'autor': 'Robert C. Martin', 'isbn': '9780132350884', 'categoria': 'Tecnologia', 'stock': 3})],
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def libro_list_create(request):
    if request.method == 'GET':
        return Response(LibroSerializer(Libro.objects.all(), many=True).data)
    if not is_admin(request.user):
        return error_response('Solo un administrador puede crear libros.', status.HTTP_403_FORBIDDEN)
    serializer = LibroSerializer(data=request.data)
    if not serializer.is_valid():
        return serialize_error(serializer)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    methods=['GET', 'PUT', 'DELETE'],
    summary='Consultar, actualizar o eliminar un libro',
    request=LibroSerializer,
    responses={200: LibroSerializer, 400: OpenApiResponse(description='Datos inválidos'), 404: OpenApiResponse(description='No encontrado')},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def libro_detail(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'GET':
        return Response(LibroSerializer(libro).data)
    if not is_admin(request.user):
        return error_response('Solo un administrador puede modificar libros.', status.HTTP_403_FORBIDDEN)
    if request.method == 'DELETE':
        libro.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = LibroSerializer(libro, data=request.data)
    if not serializer.is_valid():
        return serialize_error(serializer)
    serializer.save()
    return Response(serializer.data)


@extend_schema(
    methods=['GET', 'POST'],
    summary='Listar o registrar préstamos',
    request=PrestamoSerializer,
    responses={200: PrestamoSerializer(many=True), 201: PrestamoSerializer, 400: OpenApiResponse(description='Datos inválidos')},
    examples=[OpenApiExample('Préstamo', value={'socio': 1, 'libro': 1, 'fecha_prestamo': '2026-10-08', 'fecha_devolucion': '2026-10-15', 'estado': 'Prestado'})],
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def prestamo_list_create(request):
    if request.method == 'GET':
        prestamos = Prestamo.objects.select_related('socio', 'libro').all()
        return Response(PrestamoSerializer(prestamos, many=True).data)
    serializer = PrestamoSerializer(data=request.data)
    if not serializer.is_valid():
        return serialize_error(serializer)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    methods=['GET', 'PUT', 'DELETE'],
    summary='Consultar, actualizar o eliminar un préstamo',
    request=PrestamoSerializer,
    responses={200: PrestamoSerializer, 400: OpenApiResponse(description='Datos inválidos'), 404: OpenApiResponse(description='No encontrado')},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def prestamo_detail(request, pk):
    prestamo = get_object_or_404(Prestamo.objects.select_related('socio', 'libro'), pk=pk)
    if request.method == 'GET':
        return Response(PrestamoSerializer(prestamo).data)
    if request.method == 'DELETE':
        if not is_admin(request.user):
            return error_response('Solo un administrador puede eliminar préstamos.', status.HTTP_403_FORBIDDEN)
        prestamo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = PrestamoSerializer(prestamo, data=request.data)
    if not serializer.is_valid():
        return serialize_error(serializer)
    serializer.save()
    return Response(serializer.data)
