from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from biblioteca.models import Socio, Libro, Prestamo

class Command(BaseCommand):
    help = 'Crea los grupos de usuario (Administrador, Operador, Consulta) y asigna sus permisos'

    def handle(self, *args, **kwargs):
        grupos = ['Administrador', 'Operador', 'Consulta']
        
        for nombre_grupo in grupos:
            group, created = Group.objects.get_or_create(name=nombre_grupo)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{nombre_grupo}" creado exitosamente.'))

        # Obtener content types de los modelos
        ct_socio = ContentType.objects.get_for_model(Socio)
        ct_libro = ContentType.objects.get_for_model(Libro)
        ct_prestamo = ContentType.objects.get_for_model(Prestamo)

        # Permisos
        permisos_socio = Permission.objects.filter(content_type=ct_socio)
        permisos_libro = Permission.objects.filter(content_type=ct_libro)
        permisos_prestamo = Permission.objects.filter(content_type=ct_prestamo)

        # Asignar a Administrador (Todos los permisos)
        admin_group = Group.objects.get(name='Administrador')
        admin_group.permissions.set(list(permisos_socio) + list(permisos_libro) + list(permisos_prestamo))

        # Asignar a Operador (Crear, Modificar, Ver - Sin Eliminar)
        operador_group = Group.objects.get(name='Operador')
        op_perms = Permission.objects.filter(
            content_type__in=[ct_socio, ct_libro, ct_prestamo],
            codename__regex=r'^(add|change|view)_'
        )
        operador_group.permissions.set(op_perms)

        # Asignar a Consulta (Solo Ver)
        consulta_group = Group.objects.get(name='Consulta')
        con_perms = Permission.objects.filter(
            content_type__in=[ct_socio, ct_libro, ct_prestamo],
            codename__startswith='view_'
        )
        consulta_group.permissions.set(con_perms)

        self.stdout.write(self.style.SUCCESS('Permisos asignados correctamente a todos los grupos.'))
