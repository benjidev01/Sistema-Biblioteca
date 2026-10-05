import re
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Socio, Libro, Prestamo

def validar_rut_chileno(rut):
    # Limpiar formato
    rut_limpio = rut.replace('.', '').replace('-', '').upper().strip()
    if not re.match(r'^\d{7,8}[0-9K]$', rut_limpio):
        raise ValidationError('Ingresa un RUT válido en formato 12345678-K o sin puntos.')
    
    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]
    
    # Algoritmo Módulo 11
    suma = 0
    multiplicador = 2
    for char in reversed(cuerpo):
        suma += int(char) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    
    resto = suma % 11
    dv_esperado = 11 - resto
    if dv_esperado == 11:
        dv_calculado = '0'
    elif dv_esperado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_esperado)
        
    if dv != dv_calculado:
        raise ValidationError('El RUT ingresado no es válido (dígito verificador incorrecto).')

PREFIJOS_PAIS = [
    ('+56', 'Chile (+56)'),
    ('+54', 'Argentina (+54)'),
    ('+51', 'Perú (+51)'),
    ('+57', 'Colombia (+57)'),
    ('+52', 'México (+52)'),
    ('+1', 'EE.UU. / Canadá (+1)'),
    ('+34', 'España (+34)'),
]

class SocioForm(forms.ModelForm):
    prefijo = forms.ChoiceField(choices=PREFIJOS_PAIS, initial='+56', widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Socio
        fields = ['rut', 'nombre', 'email', 'telefono', 'foto_perfil']
        labels = {
            'rut': 'RUT / Identificación',
            'nombre': 'Nombre Completo',
            'email': 'Correo Electrónico',
            'telefono': 'Número de Teléfono',
            'foto_perfil': 'Fotografía de Perfil',
        }
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-K'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '912345678'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.telefono:
            # Intentar separar el prefijo si ya existe
            for p_code, _ in PREFIJOS_PAIS:
                if self.instance.telefono.startswith(p_code):
                    self.fields['prefijo'].initial = p_code
                    self.initial['telefono'] = self.instance.telefono[len(p_code):].strip()
                    break

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut_chileno(rut)
        # Formatear limpio
        rut_limpio = rut.replace('.', '').replace('-', '').upper().strip()
        return f"{rut_limpio[:-1]}-{rut_limpio[-1]}"

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 4:
            raise ValidationError('El nombre completo debe tener al menos 4 caracteres.')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise ValidationError('El nombre solo debe contener letras y espacios.')
        return nombre

    def clean_telefono(self):
        num = self.cleaned_data.get('telefono', '').strip()
        num_limpio = re.sub(r'\D', '', num)
        if len(num_limpio) < 8 or len(num_limpio) > 11:
            raise ValidationError('Ingresa un número de teléfono válido (entre 8 y 11 dígitos).')
        return num_limpio

    def clean(self):
        cleaned_data = super().clean()
        prefijo = cleaned_data.get('prefijo')
        telefono = cleaned_data.get('telefono')
        if prefijo and telefono:
            cleaned_data['telefono'] = f"{prefijo} {telefono}"
        return cleaned_data


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'isbn', 'categoria', 'stock', 'documento_pdf']
        labels = {
            'titulo': 'Título del Libro',
            'autor': 'Autor',
            'isbn': 'Código ISBN (13 dígitos)',
            'categoria': 'Categoría',
            'stock': 'Ejemplares en Stock',
            'documento_pdf': 'Ficha / Documento Digital (PDF)',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la obra'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del autor'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 9789563474728'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'documento_pdf': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '').strip()
        isbn_digits = re.sub(r'\D', '', isbn)
        if len(isbn_digits) != 13:
            raise ValidationError('El código ISBN debe contener exactamente 13 números.')
        return isbn_digits


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['socio', 'libro', 'fecha_prestamo', 'fecha_devolucion', 'estado', 'observaciones']
        labels = {
            'socio': 'Socio Solicitante',
            'libro': 'Libro Prestado',
            'fecha_prestamo': 'Fecha de Entrega',
            'fecha_devolucion': 'Fecha Límite de Devolución',
            'estado': 'Estado del Préstamo',
            'observaciones': 'Notas Adicionales',
        }
        widgets = {
            'socio': forms.Select(attrs={'class': 'form-select'}),
            'libro': forms.Select(attrs={'class': 'form-select'}),
            'fecha_prestamo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_devolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles o condición del libro al entregar...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        f_prestamo = cleaned_data.get('fecha_prestamo')
        f_devolucion = cleaned_data.get('fecha_devolucion')

        if f_prestamo and f_devolucion:
            if f_devolucion < f_prestamo:
                raise ValidationError('La fecha de devolución no puede ser anterior a la fecha de préstamo.')
        return cleaned_data
