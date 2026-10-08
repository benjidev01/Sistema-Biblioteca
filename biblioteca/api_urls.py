from django.urls import path

from . import api_views

app_name = 'biblioteca_api'

urlpatterns = [
    path('socios/', api_views.socio_list_create, name='socio-list'),
    path('socios/<int:pk>/', api_views.socio_detail, name='socio-detail'),
    path('libros/', api_views.libro_list_create, name='libro-list'),
    path('libros/<int:pk>/', api_views.libro_detail, name='libro-detail'),
    path('prestamos/', api_views.prestamo_list_create, name='prestamo-list'),
    path('prestamos/<int:pk>/', api_views.prestamo_detail, name='prestamo-detail'),
]
