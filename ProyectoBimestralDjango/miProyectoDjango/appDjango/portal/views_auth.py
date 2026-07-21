from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from appDjango.portal.forms import MayoristaRegistroForm, TiendaRegistroForm, TiendaLoginForm


def landing(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "perfil_mayorista"):
            return redirect("portal_mayorista_dashboard")
        if hasattr(request.user, "perfil_vendedor"):
            return redirect("portal_vendedor_dashboard")
        if hasattr(request.user, "perfil_tienda"):
            return redirect("portal_tienda_marketplace")
        if request.user.is_staff:
            return redirect("portal_admin_dashboard")

    return render(request, "portal/auth/landing.html")


def registro_mayorista(request):
    if request.method == "POST":
        formulario = MayoristaRegistroForm(request.POST)
        if formulario.is_valid():
            mayorista = formulario.guardar()
            login(request, mayorista.cuenta)
            messages.success(request, "Cuenta creada. Tu suscripción está pendiente de activación por el administrador.")
            return redirect("portal_mayorista_dashboard")
    else:
        formulario = MayoristaRegistroForm()

    return render(request, "portal/auth/registro_mayorista.html", {"formulario": formulario})


def registro_tienda(request):
    if request.method == "POST":
        formulario = TiendaRegistroForm(request.POST)
        if formulario.is_valid():
            tienda = formulario.guardar()
            login(request, tienda.cuenta)
            messages.success(request, "¡Tu tienda ha sido registrada!")
            return redirect("portal_tienda_marketplace")
    else:
        formulario = TiendaRegistroForm()

    return render(request, "portal/auth/registro_tienda.html", {"formulario": formulario})


def login_mayorista(request):
    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None and hasattr(user, "perfil_mayorista"):
            login(request, user)
            return redirect("portal_mayorista_dashboard")
        error = "Correo o contraseña incorrectos."

    return render(request, "portal/auth/login_mayorista.html", {"error": error})


def login_tienda(request):
    error = None
    if request.method == "POST":
        formulario = TiendaLoginForm(request.POST)
        if formulario.is_valid():
            user = authenticate(
                request,
                username=formulario.cleaned_data["telefono"],
                password=formulario.cleaned_data["pin"],
            )
            if user is not None and hasattr(user, "perfil_tienda"):
                login(request, user)
                return redirect("portal_tienda_marketplace")
            error = "Código inválido. Pídelo a tu mayorista."
    else:
        formulario = TiendaLoginForm()

    return render(request, "portal/auth/login_tienda.html", {"formulario": formulario, "error": error})


def login_vendedor(request):
    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None and hasattr(user, "perfil_vendedor"):
            login(request, user)
            if user.perfil_vendedor.primer_login:
                return redirect("portal_vendedor_cambiar_password")
            return redirect("portal_vendedor_dashboard")
        error = "Correo o contraseña incorrectos."

    return render(request, "portal/auth/login_vendedor.html", {"error": error})


def login_admin(request):
    error = None
    if request.method == "POST":
        formulario = AuthenticationForm(request=request, data=request.POST)
        if formulario.is_valid():
            username = formulario.cleaned_data.get("username")
            password = formulario.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect("portal_admin_dashboard")
            error = "Credenciales incorrectas o cuenta sin permisos de administrador."
    else:
        formulario = AuthenticationForm()

    return render(request, "portal/auth/login_admin.html", {"formulario": formulario, "error": error})


def logout_portal(request):
    logout(request)
    messages.info(request, "Has salido del sistema.")
    return redirect("portal_landing")
