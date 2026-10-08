from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Libro, Prestamo, Socio


class BibliotecaApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username='admin',
            password='AdminPassword123!',
            is_staff=True,
        )
        self.user = user_model.objects.create_user(
            username='lector',
            password='UserPassword123!',
        )
        self.socio = Socio.objects.create(
            rut='12345678-5',
            nombre='Ana Pérez',
            email='ana@example.com',
            telefono='+56 912345678',
        )
        self.libro = Libro.objects.create(
            titulo='Clean Code',
            autor='Robert C. Martin',
            isbn='9780132350884',
            categoria='Tecnologia',
            stock=3,
        )

    def authenticate(self, username='admin', password='AdminPassword123!'):
        response = self.client.post(
            '/api/token/',
            {'username': username, 'password': password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response

    def test_endpoints_require_jwt(self):
        response = self.client.get('/api/libros/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_obtain_and_refresh(self):
        token_response = self.authenticate()
        refresh_response = self.client.post(
            '/api/token/refresh/',
            {'refresh': token_response.data['refresh']},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_regular_user_cannot_see_private_socio_fields(self):
        self.authenticate('lector', 'UserPassword123!')
        response = self.client.get('/api/socios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('email', response.data[0])
        self.assertNotIn('telefono', response.data[0])

    def test_admin_can_create_update_and_delete_book(self):
        self.authenticate()
        response = self.client.post(
            '/api/libros/',
            {
                'titulo': 'Django for APIs',
                'autor': 'William S. Vincent',
                'isbn': '9781735467221',
                'categoria': 'Tecnologia',
                'stock': 2,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        book_id = response.data['id']

        response = self.client.put(
            f'/api/libros/{book_id}/',
            {
                'titulo': 'Django for APIs 2',
                'autor': 'William S. Vincent',
                'isbn': '9781735467221',
                'categoria': 'Tecnologia',
                'stock': 4,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(f'/api/libros/{book_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_modify_books(self):
        self.authenticate('lector', 'UserPassword123!')
        response = self.client.put(
            f'/api/libros/{self.libro.pk}/',
            {
                'titulo': 'No autorizado',
                'autor': self.libro.autor,
                'isbn': self.libro.isbn,
                'categoria': self.libro.categoria,
                'stock': self.libro.stock,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_loan_crud_and_date_validation(self):
        self.authenticate()
        invalid = self.client.post(
            '/api/prestamos/',
            {
                'socio': self.socio.pk,
                'libro': self.libro.pk,
                'fecha_prestamo': date.today().isoformat(),
                'fecha_devolucion': (date.today() - timedelta(days=1)).isoformat(),
                'estado': 'Prestado',
            },
            format='json',
        )
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

        created = self.client.post(
            '/api/prestamos/',
            {
                'socio': self.socio.pk,
                'libro': self.libro.pk,
                'fecha_prestamo': date.today().isoformat(),
                'fecha_devolucion': (date.today() + timedelta(days=7)).isoformat(),
                'estado': 'Prestado',
            },
            format='json',
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        loan_id = created.data['id']

        listed = self.client.get('/api/prestamos/')
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data[0]['socio_nombre'], self.socio.nombre)

        deleted = self.client.delete(f'/api/prestamos/{loan_id}/')
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
