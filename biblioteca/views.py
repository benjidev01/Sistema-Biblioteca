from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from .models import Socio, Libro, Prestamo
from .forms import SocioForm, LibroForm, PrestamoForm

# --- INICIO DE SESIÓN Y LOGOUT ---
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('biblioteca:home')
    
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            messages.success(request, f"¡Bienvenido/a {user.username}!")
            return redirect('biblioteca:home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    
    return render(request, 'auth/login.html')


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('biblioteca:login')


# --- DASHBOARD PRINCIPAL ---
@login_required
def home(request):
    context = {
        'total_socios': Socio.objects.count(),
        'total_libros': Libro.objects.count(),
        'total_prestamos': Prestamo.objects.count(),
        'prestamos_activos': Prestamo.objects.filter(estado='Prestado').count(),
    }
    return render(request, 'home.html', context)


# ==========================================
# --- CRUD SOCIOS ---
# ==========================================
@login_required
@permission_required('biblioteca.view_socio', raise_exception=True)
def socio_list(request):
    query = request.GET.get('q', '')
    if query:
        socios = Socio.objects.filter(Q(nombre__icontains=query) | Q(rut__icontains=query) | Q(email__icontains=query))
    else:
        socios = Socio.objects.all()
    return render(request, 'socios/socio_list.html', {'socios': socios, 'query': query})


@login_required
@permission_required('biblioteca.add_socio', raise_exception=True)
def socio_create(request):
    if request.method == 'POST':
        form = SocioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Socio registrado con éxito.")
            return redirect('biblioteca:socio_list')
    else:
        form = SocioForm()
    return render(request, 'socios/socio_form.html', {'form': form, 'title': 'Registrar Nuevo Socio'})


@login_required
@permission_required('biblioteca.change_socio', raise_exception=True)
def socio_update(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        form = SocioForm(request.POST, request.FILES, instance=socio)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos del socio actualizados.")
            return redirect('biblioteca:socio_list')
    else:
        form = SocioForm(instance=socio)
    return render(request, 'socios/socio_form.html', {'form': form, 'title': f'Editar Socio: {socio.nombre}'})


@login_required
@permission_required('biblioteca.delete_socio', raise_exception=True)
def socio_delete(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        socio.delete()
        messages.success(request, "Socio eliminado correctamente.")
        return redirect('biblioteca:socio_list')
    return render(request, 'common/confirm_delete.html', {'object': socio, 'type': 'Socio', 'cancel_url': 'biblioteca:socio_list'})


# ==========================================
# --- CRUD LIBROS ---
# ==========================================
@login_required
@permission_required('biblioteca.view_libro', raise_exception=True)
def libro_list(request):
    query = request.GET.get('q', '')
    if query:
        libros = Libro.objects.filter(Q(titulo__icontains=query) | Q(autor__icontains=query) | Q(isbn__icontains=query) | Q(categoria__icontains=query))
    else:
        libros = Libro.objects.all()
    return render(request, 'libros/libro_list.html', {'libros': libros, 'query': query})


@login_required
@permission_required('biblioteca.add_libro', raise_exception=True)
def libro_create(request):
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Libro agregado exitosamente al catálogo.")
            return redirect('biblioteca:libro_list')
    else:
        form = LibroForm()
    return render(request, 'libros/libro_form.html', {'form': form, 'title': 'Agregar Nuevo Libro'})


@login_required
@permission_required('biblioteca.change_libro', raise_exception=True)
def libro_update(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, "Libro actualizado.")
            return redirect('biblioteca:libro_list')
    else:
        form = LibroForm(instance=libro)
    return render(request, 'libros/libro_form.html', {'form': form, 'title': f'Editar Libro: {libro.titulo}'})


@login_required
@permission_required('biblioteca.delete_libro', raise_exception=True)
def libro_delete(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        libro.delete()
        messages.success(request, "Libro eliminado correctamente.")
        return redirect('biblioteca:libro_list')
    return render(request, 'common/confirm_delete.html', {'object': libro, 'type': 'Libro', 'cancel_url': 'biblioteca:libro_list'})


# ==========================================
# --- CRUD PRÉSTAMOS (TRANSACCIONAL) ---
# ==========================================
@login_required
@permission_required('biblioteca.view_prestamo', raise_exception=True)
def prestamo_list(request):
    query = request.GET.get('q', '')
    if query:
        prestamos = Prestamo.objects.filter(Q(socio__nombre__icontains=query) | Q(libro__titulo__icontains=query) | Q(estado__icontains=query))
    else:
        prestamos = Prestamo.objects.all()
    return render(request, 'prestamos/prestamo_list.html', {'prestamos': prestamos, 'query': query})


@login_required
@permission_required('biblioteca.add_prestamo', raise_exception=True)
def prestamo_create(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Préstamo registrado exitosamente.")
            return redirect('biblioteca:prestamo_list')
    else:
        form = PrestamoForm()
    return render(request, 'prestamos/prestamo_form.html', {'form': form, 'title': 'Registrar Nuevo Préstamo'})


@login_required
@permission_required('biblioteca.change_prestamo', raise_exception=True)
def prestamo_update(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.method == 'POST':
        form = PrestamoForm(request.POST, instance=prestamo)
        if form.is_valid():
            form.save()
            messages.success(request, "Préstamo actualizado.")
            return redirect('biblioteca:prestamo_list')
    else:
        form = PrestamoForm(instance=prestamo)
    return render(request, 'prestamos/prestamo_form.html', {'form': form, 'title': f'Editar Préstamo #{prestamo.id}'})


@login_required
@permission_required('biblioteca.delete_prestamo', raise_exception=True)
def prestamo_delete(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.method == 'POST':
        prestamo.delete()
        messages.success(request, "Préstamo eliminado.")
        return redirect('biblioteca:prestamo_list')
    return render(request, 'common/confirm_delete.html', {'object': prestamo, 'type': 'Préstamo', 'cancel_url': 'biblioteca:prestamo_list'})
