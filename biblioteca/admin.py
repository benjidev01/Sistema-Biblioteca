from django.contrib import admin
from .models import Socio, Libro, Prestamo

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'email', 'telefono', 'fecha_registro', 'tiene_foto')
    search_fields = ('rut', 'nombre', 'email')
    list_filter = ('fecha_registro',)
    ordering = ('nombre',)

    def tiene_foto(self, obj):
        return "Sí" if obj.foto_perfil else "No"
    tiene_foto.short_description = "Foto"


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'titulo', 'autor', 'categoria', 'stock', 'tiene_pdf')
    search_fields = ('titulo', 'autor', 'isbn')
    list_filter = ('categoria',)
    ordering = ('titulo',)

    def tiene_pdf(self, obj):
        return "Sí" if obj.documento_pdf else "No"
    tiene_pdf.short_description = "PDF Adjunto"


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'socio', 'libro', 'fecha_prestamo', 'fecha_devolucion', 'estado')
    search_fields = ('socio__nombre', 'socio__rut', 'libro__titulo', 'libro__isbn')
    list_filter = ('estado', 'fecha_prestamo', 'fecha_devolucion')
    ordering = ('-fecha_prestamo',)
    autocomplete_fields = ['socio', 'libro']
