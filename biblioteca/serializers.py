from rest_framework import serializers

from .models import Libro, Prestamo, Socio


class SocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socio
        fields = (
            'id', 'rut', 'nombre', 'email', 'telefono',
            'foto_perfil', 'fecha_registro',
        )
        read_only_fields = ('id', 'fecha_registro')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not (user.is_staff or user.is_superuser):
            data.pop('email', None)
            data.pop('telefono', None)
        return data

    def validate_nombre(self, value):
        value = value.strip()
        if len(value) < 4:
            raise serializers.ValidationError('El nombre debe tener al menos 4 caracteres.')
        return value


class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = (
            'id', 'titulo', 'autor', 'isbn', 'categoria',
            'documento_pdf', 'stock',
        )
        read_only_fields = ('id',)

    def validate_isbn(self, value):
        isbn = ''.join(char for char in value if char.isdigit())
        if len(isbn) not in (10, 13):
            raise serializers.ValidationError('El ISBN debe contener 10 o 13 dígitos.')
        return isbn

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return value


class PrestamoSerializer(serializers.ModelSerializer):
    socio_nombre = serializers.CharField(source='socio.nombre', read_only=True)
    libro_titulo = serializers.CharField(source='libro.titulo', read_only=True)

    class Meta:
        model = Prestamo
        fields = (
            'id', 'socio', 'socio_nombre', 'libro', 'libro_titulo',
            'fecha_prestamo', 'fecha_devolucion', 'estado', 'observaciones',
        )
        read_only_fields = ('id', 'socio_nombre', 'libro_titulo')

    def validate(self, attrs):
        fecha_prestamo = attrs.get(
            'fecha_prestamo',
            getattr(self.instance, 'fecha_prestamo', None),
        )
        fecha_devolucion = attrs.get(
            'fecha_devolucion',
            getattr(self.instance, 'fecha_devolucion', None),
        )
        if fecha_prestamo and fecha_devolucion and fecha_devolucion < fecha_prestamo:
            raise serializers.ValidationError({
                'fecha_devolucion': (
                    'La fecha de devolución no puede ser anterior '
                    'a la fecha de préstamo.'
                ),
            })
        return attrs
