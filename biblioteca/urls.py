from django.urls import path
from . import views

app_name = 'biblioteca'

urlpatterns = [
    # Autenticación y Home
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.home, name='home'),

    # CRUD Socios
    path('socios/', views.socio_list, name='socio_list'),
    path('socios/nuevo/', views.socio_create, name='socio_create'),
    path('socios/<int:pk>/editar/', views.socio_update, name='socio_update'),
    path('socios/<int:pk>/eliminar/', views.socio_delete, name='socio_delete'),

    # CRUD Libros
    path('libros/', views.libro_list, name='libro_list'),
    path('libros/nuevo/', views.libro_create, name='libro_create'),
    path('libros/<int:pk>/editar/', views.libro_update, name='libro_update'),
    path('libros/<int:pk>/eliminar/', views.libro_delete, name='libro_delete'),

    # CRUD Préstamos
    path('prestamos/', views.prestamo_list, name='prestamo_list'),
    path('prestamos/nuevo/', views.prestamo_create, name='prestamo_create'),
    path('prestamos/<int:pk>/editar/', views.prestamo_update, name='prestamo_update'),
    path('prestamos/<int:pk>/eliminar/', views.prestamo_delete, name='prestamo_delete'),
]
