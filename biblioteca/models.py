from django.db import models
from django.core.validators import FileExtensionValidator

class Socio(models.Model):
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    foto_perfil = models.ImageField(upload_to='socios/', null=True, blank=True, verbose_name="Foto de Perfil")
    fecha_registro = models.DateField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Socio"
        verbose_name_plural = "Socios"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class Libro(models.Model):
    CATEGORIAS = [
        ('Novela', 'Novela'),
        ('Ciencia', 'Ciencia'),
        ('Historia', 'Historia'),
        ('Tecnologia', 'Tecnología'),
        ('Infantil', 'Infantil'),
        ('General', 'General'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título")
    autor = models.CharField(max_length=150, verbose_name="Autor")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='General', verbose_name="Categoría")
    documento_pdf = models.FileField(
        upload_to='libros_pdf/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name="Documento PDF / Ficha"
    )
    stock = models.PositiveIntegerField(default=1, verbose_name="Stock Disponible")

    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['titulo']

    def __str__(self):
        return f"{self.titulo} - {self.autor}"


class Prestamo(models.Model):
    ESTADOS = [
        ('Prestado', 'Prestado'),
        ('Devuelto', 'Devuelto'),
        ('Atrasado', 'Atrasado'),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='prestamos', verbose_name="Socio")
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='prestamos', verbose_name="Libro")
    fecha_prestamo = models.DateField(verbose_name="Fecha de Préstamo")
    fecha_devolucion = models.DateField(verbose_name="Fecha de Devolución")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Prestado', verbose_name="Estado")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']

    def __str__(self):
        return f"Préstamo #{self.id}: {self.libro.titulo} -> {self.socio.nombre}"
