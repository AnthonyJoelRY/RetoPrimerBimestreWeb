from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User, Group
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from functools import wraps

# Django REST Framework
from rest_framework import viewsets
from rest_framework import permissions

# Serializers
from appDjango.serializers import (
    UserSerializer,
    GroupSerializer,
    MayoristaSerializer,
    VendedorSerializer,
    TiendaSerializer,
    ProductoSerializer,
    PedidoSerializer,
    PedidoItemSerializer,
    PagoSerializer,
    RendicionSerializer,
)

# Modelos
from appDjango.models import (
    Mayorista,
    Vendedor,
    Tienda,
    Producto,
    Pedido,
    PedidoItem,
    Pago,
    Rendicion,
)

# Formularios
from appDjango.forms import (
    AdminLoginForm,
    AgregarCarritoForm,
    LoginEmailForm,
    MayoristaRegistroForm,
    MayoristaConfigComercialForm,
    PedidoVendedorPagoForm,
    TiendaRegistroForm,
    TiendaLoginForm,
    VendedorCrearForm,
    ProductoMayoristaForm,
    AjusteStockForm,
    PedidoEntregaForm,
)

STOCK_CRITICO = 10
CARRITO_VENDEDOR_SESSION_KEY = "vendedor_carrito"
CARRITO_TIENDA_SESSION_KEY = "tienda_carrito"


# ===================== Decoradores de acceso por rol =====================


def mayorista_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(
            request.user,
            "perfil_mayorista",
        ):
            return redirect("portal_login_mayorista")

        mayorista = request.user.perfil_mayorista

        if mayorista.estado == "pendiente_pago":
            nombre_empresa = mayorista.nombre

            logout(request)

            request.session["mayorista_registrado_nombre"] = nombre_empresa

            return redirect("portal_registro_mayorista_confirmacion")

        if mayorista.estado == "suspendido":
            logout(request)

            request.session["mayorista_login_error"] = (
                "Tu cuenta está suspendida. " "Comunícate con el administrador."
            )

            return redirect("portal_login_mayorista")

        request.mayorista = mayorista

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapper


def vendedor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(
            request.user, "perfil_vendedor"
        ):
            return redirect("portal_login_vendedor")
        vendedor = request.user.perfil_vendedor
        if vendedor.primer_login and view_func.__name__ != "vendedor_cambiar_password":
            return redirect("portal_vendedor_cambiar_password")
        request.vendedor = vendedor
        return view_func(request, *args, **kwargs)

    return wrapper


def tienda_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(
            request.user, "perfil_tienda"
        ):
            return redirect("portal_login_tienda")
        request.tienda = request.user.perfil_tienda
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("portal_login_admin")
        return view_func(request, *args, **kwargs)

    return wrapper


# ===================== Autenticación y landing =====================


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

    return render(request, "auth/landing.html")


def registro_mayorista(request):
    if request.method == "POST":
        formulario = MayoristaRegistroForm(request.POST)

        if formulario.is_valid():
            mayorista = formulario.guardar()

            request.session["mayorista_registrado_nombre"] = mayorista.nombre

            return redirect("portal_registro_mayorista_confirmacion")
    else:
        formulario = MayoristaRegistroForm()

    return render(
        request,
        "auth/registro_mayorista.html",
        {
            "formulario": formulario,
        },
    )


def registro_mayorista_confirmacion(request):
    nombre_empresa = request.session.get(
        "mayorista_registrado_nombre",
        "",
    )

    return render(
        request,
        "auth/registro_mayorista_confirmacion.html",
        {
            "nombre_empresa": nombre_empresa,
        },
    )


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

    return render(request, "auth/registro_tienda.html", {"formulario": formulario})


def login_mayorista(request):
    error = request.session.pop(
        "mayorista_login_error",
        None,
    )

    if request.method == "POST":
        formulario = LoginEmailForm(request.POST)

        if formulario.is_valid():
            user = authenticate(
                request,
                username=formulario.cleaned_data["email"],
                password=formulario.cleaned_data["password"],
            )

            if user is not None and hasattr(
                user,
                "perfil_mayorista",
            ):
                mayorista = user.perfil_mayorista

                if mayorista.estado == "pendiente_pago":
                    request.session["mayorista_registrado_nombre"] = mayorista.nombre

                    return redirect("portal_registro_mayorista_confirmacion")

                if mayorista.estado == "suspendido":
                    error = (
                        "Tu cuenta está suspendida. " "Comunícate con el administrador."
                    )

                else:
                    login(request, user)

                    return redirect("portal_mayorista_dashboard")

            else:
                error = "Correo o contraseña incorrectos."
    else:
        formulario = LoginEmailForm()

    return render(
        request,
        "auth/login_mayorista.html",
        {
            "formulario": formulario,
            "error": error,
        },
    )


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

    return render(
        request, "auth/login_tienda.html", {"formulario": formulario, "error": error}
    )


def login_vendedor(request):
    error = None
    if request.method == "POST":
        formulario = LoginEmailForm(request.POST)
        if formulario.is_valid():
            user = authenticate(
                request,
                username=formulario.cleaned_data["email"],
                password=formulario.cleaned_data["password"],
            )
            if user is not None and hasattr(user, "perfil_vendedor"):
                if not user.perfil_vendedor.activo:
                    error = "Tu cuenta está desactivada. Contacta a tu mayorista."
                else:
                    login(request, user)
                    if user.perfil_vendedor.primer_login:
                        return redirect("portal_vendedor_cambiar_password")
                    return redirect("portal_vendedor_dashboard")
            else:
                error = "Correo o contraseña incorrectos."
    else:
        formulario = LoginEmailForm()

    return render(
        request, "auth/login_vendedor.html", {"formulario": formulario, "error": error}
    )


def login_admin(request):
    error = None
    if request.method == "POST":
        formulario = AdminLoginForm(request=request, data=request.POST)
        if formulario.is_valid():
            user = formulario.get_user()
            if user.is_staff:
                login(request, user)
                return redirect("portal_admin_dashboard")
            error = "Credenciales incorrectas o cuenta sin permisos de administrador."
    else:
        formulario = AdminLoginForm()

    return render(
        request, "auth/login_admin.html", {"formulario": formulario, "error": error}
    )


def logout_portal(request):
    logout(request)
    return redirect("portal_landing")


# ===================== Mayorista =====================


@mayorista_required
def mayorista_dashboard(request):
    contexto = request.mayorista.obtener_resumen_dashboard()

    return render(
        request,
        "mayorista/dashboard.html",
        contexto,
    )


@mayorista_required
def mayorista_productos(request):
    productos = Producto.objects.filter(mayorista=request.mayorista).order_by("-id")
    return render(request, "mayorista/productos.html", {"productos": productos})


@mayorista_required
def mayorista_producto_crear(request):
    if request.method == "POST":
        formulario = ProductoMayoristaForm(request.POST)
        if formulario.is_valid():
            producto = formulario.save(commit=False)
            producto.mayorista = request.mayorista
            producto.save()
            messages.success(request, "Producto creado correctamente.")
            return redirect("portal_mayorista_productos")
    else:
        formulario = ProductoMayoristaForm()

    return render(
        request,
        "mayorista/producto_form.html",
        {"formulario": formulario, "titulo": "Nuevo producto"},
    )


@mayorista_required
def mayorista_producto_editar(request, id):
    producto = get_object_or_404(Producto, pk=id, mayorista=request.mayorista)

    if request.method == "POST":
        formulario = ProductoMayoristaForm(request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto actualizado.")
            return redirect("portal_mayorista_productos")
    else:
        formulario = ProductoMayoristaForm(instance=producto)

    return render(
        request,
        "mayorista/producto_form.html",
        {"formulario": formulario, "titulo": "Editar producto"},
    )


@mayorista_required
def mayorista_producto_eliminar(request, id):
    producto = get_object_or_404(Producto, pk=id, mayorista=request.mayorista)
    producto.delete()
    messages.success(request, "Producto eliminado.")
    return redirect("portal_mayorista_productos")


@mayorista_required
def mayorista_inventario(request):
    if request.method == "POST":
        producto = get_object_or_404(
            Producto, pk=request.POST.get("producto_id"), mayorista=request.mayorista
        )
        formulario = AjusteStockForm(request.POST)
        if formulario.is_valid():
            producto.stock = formulario.cleaned_data["stock"]
            producto.save(update_fields=["stock"])
            messages.success(request, "Stock de %s actualizado." % producto.nombre)
        return redirect("portal_mayorista_inventario")

    # Los productos con menos stock primero: lo urgente arriba
    productos = Producto.objects.filter(mayorista=request.mayorista).order_by(
        "stock", "nombre"
    )

    total_productos = productos.count()
    criticos = productos.filter(stock__lt=STOCK_CRITICO).count()

    return render(
        request,
        "mayorista/inventario.html",
        {
            "productos": productos,
            "stock_critico": STOCK_CRITICO,
            "total_productos": total_productos,
            "criticos": criticos,
        },
    )


@mayorista_required
def mayorista_pedidos(request):
    estado = request.GET.get("estado", "")
    pedidos = (
        Pedido.objects.filter(mayorista=request.mayorista)
        .select_related("tienda", "vendedor")
        .prefetch_related("items__producto")
        .order_by("-creado_en")
    )
    if estado:
        pedidos = pedidos.filter(estado=estado)

    return render(
        request,
        "mayorista/pedidos.html",
        {
            "pedidos": pedidos,
            "estado_seleccionado": estado,
            "estados": Pedido.ESTADO_CHOICES,
        },
    )


@mayorista_required
def mayorista_pedido_transicion(request, id, accion):
    pedido = get_object_or_404(
        Pedido,
        pk=id,
        mayorista=request.mayorista,
    )

    try:
        pedido.aplicar_transicion(accion)

    except ValueError as error:
        messages.error(
            request,
            str(error),
        )

        return redirect("portal_mayorista_pedidos")

    messages.success(
        request,
        "Pedido #%s actualizado." % pedido.id,
    )

    return redirect("portal_mayorista_pedidos")


@mayorista_required
def mayorista_vendedores(request):
    vendedores = Vendedor.objects.filter(mayorista=request.mayorista).order_by("nombre")
    return render(request, "mayorista/vendedores.html", {"vendedores": vendedores})


@mayorista_required
def mayorista_vendedor_crear(request):
    if request.method == "POST":
        formulario = VendedorCrearForm(request.POST, mayorista=request.mayorista)
        if formulario.is_valid():
            formulario.guardar()
            messages.success(
                request,
                "Vendedor creado. Contraseña inicial: %s (se le pedirá cambiarla al ingresar)."
                % VendedorCrearForm.CONTRASENA_INICIAL,
            )
            return redirect("portal_mayorista_vendedores")
    else:
        formulario = VendedorCrearForm(mayorista=request.mayorista)

    return render(request, "mayorista/vendedor_form.html", {"formulario": formulario})


@mayorista_required
def mayorista_vendedor_toggle(request, id):
    vendedor = get_object_or_404(Vendedor, pk=id, mayorista=request.mayorista)
    vendedor.activo = not vendedor.activo
    vendedor.save(update_fields=["activo"])

    if vendedor.activo:
        messages.success(
            request, "%s fue reactivado y ya puede iniciar sesión." % vendedor.nombre
        )
    else:
        messages.info(request, "%s fue desactivado." % vendedor.nombre)

    return redirect("portal_mayorista_vendedores")


@mayorista_required
def mayorista_rendiciones(request):
    rendiciones = (
        Rendicion.objects.filter(mayorista=request.mayorista)
        .select_related("vendedor")
        .order_by("-id")
    )

    pendientes_qs = rendiciones.filter(estado="pendiente")
    total_pendiente = sum(r.calcular_total_neto() for r in pendientes_qs)

    return render(
        request,
        "mayorista/rendiciones.html",
        {
            "rendiciones": rendiciones,
            "pendientes": pendientes_qs.count(),
            "total_pendiente": total_pendiente,
        },
    )


@mayorista_required
def mayorista_rendicion_confirmar(request, id):
    rendicion = get_object_or_404(Rendicion, pk=id, mayorista=request.mayorista)
    rendicion.estado = "confirmado"
    rendicion.save(update_fields=["estado"])
    messages.success(request, "Rendición confirmada.")
    return redirect("portal_mayorista_rendiciones")


@mayorista_required
def mayorista_reportes(request):
    contexto = request.mayorista.obtener_reporte_comercial()

    return render(
        request,
        "mayorista/reportes.html",
        contexto,
    )


@mayorista_required
def mayorista_mi_cuenta(request):
    if request.method == "POST":
        formulario = PasswordChangeForm(user=request.user, data=request.POST)
        if formulario.is_valid():
            formulario.save()
            update_session_auth_hash(request, formulario.user)
            messages.success(request, "Contraseña actualizada.")
            return redirect("portal_mayorista_mi_cuenta")
    else:
        formulario = PasswordChangeForm(user=request.user)

    return render(
        request,
        "mayorista/mi_cuenta.html",
        {"formulario": formulario, "mayorista": request.mayorista},
    )


# ===================== Vendedor =====================


@vendedor_required
def vendedor_dashboard(request):
    contexto = request.vendedor.obtener_resumen_dashboard()

    return render(
        request,
        "vendedor/dashboard.html",
        contexto,
    )


@vendedor_required
def vendedor_cambiar_password(request):
    if request.method == "POST":
        formulario = SetPasswordForm(user=request.user, data=request.POST)
        if formulario.is_valid():
            formulario.save()
            update_session_auth_hash(request, formulario.user)
            vendedor = request.user.perfil_vendedor
            vendedor.primer_login = False
            vendedor.save(update_fields=["primer_login"])
            messages.success(
                request, "Contraseña actualizada. Ya puedes usar la plataforma."
            )
            return redirect("portal_vendedor_dashboard")
    else:
        formulario = SetPasswordForm(user=request.user)

    return render(request, "vendedor/cambiar_password.html", {"formulario": formulario})


@vendedor_required
def vendedor_pedido_paso1(request):
    request.session.pop(CARRITO_VENDEDOR_SESSION_KEY, None)
    busqueda = request.GET.get("q", "")
    tiendas = Tienda.objects.none()
    if busqueda:
        tiendas = Tienda.objects.filter(
            Q(nombre__icontains=busqueda) | Q(telefono__icontains=busqueda)
        )

    return render(
        request,
        "vendedor/pedido_paso1.html",
        {"busqueda": busqueda, "tiendas": tiendas},
    )


@vendedor_required
def vendedor_pedido_paso2(request, tienda_id):
    tienda = get_object_or_404(Tienda, pk=tienda_id)
    productos = request.vendedor.obtener_productos_disponibles()
    carrito = request.session.get(CARRITO_VENDEDOR_SESSION_KEY, {})

    if request.method == "POST":
        nuevo_carrito = {}
        errores = []

        for producto in productos:
            crudo = request.POST.get("cantidad_%s" % producto.id, 0)
            try:
                cantidad = int(crudo or 0)
            except (TypeError, ValueError):
                cantidad = 0

            if cantidad <= 0:
                continue

            if not producto.verificar_minimo_compra(cantidad):
                errores.append(
                    "%s requiere un mínimo de %s unidades."
                    % (producto.nombre, producto.minimo_compra)
                )
            elif not producto.verificar_stock(cantidad):
                errores.append(
                    "Solo hay %s unidades de %s." % (producto.stock, producto.nombre)
                )
            else:
                nuevo_carrito[str(producto.id)] = cantidad

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect("portal_vendedor_pedido_paso2", tienda_id=tienda.id)

        if not nuevo_carrito:
            messages.error(request, "Selecciona al menos un producto.")
            return redirect("portal_vendedor_pedido_paso2", tienda_id=tienda.id)

        request.session[CARRITO_VENDEDOR_SESSION_KEY] = nuevo_carrito
        request.session["vendedor_tienda_id"] = tienda.id
        return redirect("portal_vendedor_pedido_paso3")

    filas = [
        {"producto": producto, "cantidad": carrito.get(str(producto.id), 0)}
        for producto in productos
    ]

    return render(
        request,
        "vendedor/pedido_paso2.html",
        {
            "tienda": tienda,
            "filas": filas,
        },
    )


@vendedor_required
def vendedor_pedido_paso3(request):
    tienda_id = request.session.get("vendedor_tienda_id")
    carrito = request.session.get(CARRITO_VENDEDOR_SESSION_KEY, {})
    tienda = get_object_or_404(Tienda, pk=tienda_id) if tienda_id else None

    if not tienda or not carrito:
        messages.error(request, "Selecciona una tienda y productos antes de continuar.")
        return redirect("portal_vendedor_pedido_paso1")

    productos = {p.id: p for p in Producto.objects.filter(pk__in=carrito.keys())}
    lineas = []
    total = 0
    for producto_id, cantidad in carrito.items():
        producto = productos[int(producto_id)]
        subtotal = producto.precio * cantidad
        total += subtotal
        lineas.append(
            {"producto": producto, "cantidad": cantidad, "subtotal": subtotal}
        )

    if request.method == "POST":
        formulario = PedidoVendedorPagoForm(request.POST)
        if formulario.is_valid():
            try:
                pedido = Pedido.crear_validado(
                    tienda=tienda,
                    mayorista=request.vendedor.mayorista,
                    vendedor=request.vendedor,
                    creado_por="vendedor",
                    tipo_pago=formulario.cleaned_data["tipo_pago"],
                    lineas=lineas,
                    telefono_contacto=tienda.telefono or "",
                )
            except ValueError as error:
                messages.error(request, str(error))
                return redirect("portal_vendedor_pedido_paso3")

            request.session.pop(CARRITO_VENDEDOR_SESSION_KEY, None)
            request.session.pop("vendedor_tienda_id", None)
            messages.success(
                request, "Pedido #%s registrado correctamente." % pedido.id
            )
            return redirect("portal_vendedor_dashboard")
    else:
        formulario = PedidoVendedorPagoForm()

    return render(
        request,
        "vendedor/pedido_paso3.html",
        {
            "tienda": tienda,
            "lineas": lineas,
            "total": total,
            "formulario": formulario,
        },
    )


@vendedor_required
def vendedor_cobros(request):
    pagos = Pago.objects.filter(
        pedido__vendedor=request.vendedor, metodo="efectivo", estado="pendiente"
    ).select_related("pedido", "pedido__tienda")

    return render(request, "vendedor/cobros.html", {"pagos": pagos})


@vendedor_required
def vendedor_marcar_cobrado(request, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id, pedido__vendedor=request.vendedor)
    pago.estado = "confirmado"
    pago.save(update_fields=["estado"])
    pago.pedido.cobro_confirmado = True
    pago.pedido.save(update_fields=["cobro_confirmado"])
    messages.success(request, "Cobro registrado.")
    return redirect("portal_vendedor_cobros")


@vendedor_required
def vendedor_rendicion(request):
    vendedor = request.vendedor

    pagos_por_rendir = Rendicion.obtener_pagos_por_rendir(vendedor)

    if request.method == "POST":
        try:
            Rendicion.crear_para_vendedor(vendedor)

        except ValueError as error:
            messages.error(
                request,
                str(error),
            )

            return redirect("portal_vendedor_rendicion")

        messages.success(
            request,
            "Rendición enviada al mayorista.",
        )

        return redirect("portal_vendedor_dashboard")

    total = Rendicion.calcular_total_por_rendir(vendedor)

    return render(
        request,
        "vendedor/rendicion.html",
        {
            "pagos": pagos_por_rendir,
            "total": total,
        },
    )


# ===================== Tienda =====================


def _carrito_tienda(request):
    return request.session.get(
        CARRITO_TIENDA_SESSION_KEY, {"mayorista_id": None, "items": {}}
    )


@tienda_required
def tienda_marketplace(request):
    mayoristas = Mayorista.objects.filter(estado="activo").order_by("nombre")
    return render(request, "tienda/marketplace.html", {"mayoristas": mayoristas})


@tienda_required
def tienda_catalogo(request, mayorista_id):
    mayorista = get_object_or_404(Mayorista, pk=mayorista_id, estado="activo")
    productos = Producto.objects.filter(mayorista=mayorista, activo=True).order_by(
        "nombre"
    )

    carrito = _carrito_tienda(request)
    en_este_carrito = (
        carrito["items"] if carrito.get("mayorista_id") == mayorista.id else {}
    )

    # Resumen para la barra flotante del carrito
    carrito_unidades = sum(en_este_carrito.values())
    precios = {str(p.id): p.precio for p in productos}
    carrito_total = sum(
        precios.get(pid, 0) * cantidad for pid, cantidad in en_este_carrito.items()
    )

    return render(
        request,
        "tienda/catalogo.html",
        {
            "mayorista": mayorista,
            "productos": productos,
            "carrito": en_este_carrito,
            "carrito_unidades": carrito_unidades,
            "carrito_total": carrito_total,
        },
    )


@tienda_required
def tienda_agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)

    formulario = AgregarCarritoForm(request.POST, producto=producto)
    if not formulario.is_valid():
        for error in formulario.errors["cantidad"]:
            messages.error(request, error)
        return redirect("portal_tienda_catalogo", mayorista_id=producto.mayorista_id)

    cantidad = formulario.cleaned_data["cantidad"]

    carrito = _carrito_tienda(request)
    if carrito.get("mayorista_id") not in (None, producto.mayorista_id):
        carrito = {"mayorista_id": None, "items": {}}
        messages.info(request, "Se reinició tu carrito porque cambiaste de mayorista.")

    carrito["mayorista_id"] = producto.mayorista_id
    items = carrito.get("items", {})
    nueva_cantidad = items.get(str(producto.id), 0) + cantidad

    if not producto.verificar_stock(nueva_cantidad):
        messages.error(
            request,
            "Ya tienes %s unidades en el carrito y solo hay %s disponibles."
            % (items.get(str(producto.id), 0), producto.stock),
        )
        return redirect("portal_tienda_catalogo", mayorista_id=producto.mayorista_id)

    items[str(producto.id)] = nueva_cantidad
    carrito["items"] = items
    request.session[CARRITO_TIENDA_SESSION_KEY] = carrito

    messages.success(request, "%s agregado al carrito." % producto.nombre)
    return redirect("portal_tienda_catalogo", mayorista_id=producto.mayorista_id)


@tienda_required
def tienda_carrito(request):
    carrito = _carrito_tienda(request)
    items = carrito.get("items", {})
    productos = {p.id: p for p in Producto.objects.filter(pk__in=items.keys())}

    if request.method == "POST":
        for clave in list(items.keys()):
            accion = request.POST.get("accion_%s" % clave)
            producto = productos.get(int(clave))
            if producto is None or accion == "quitar":
                if accion == "quitar" or producto is None:
                    items.pop(clave, None)
                continue
            if accion == "sumar":
                if producto.verificar_stock(items[clave] + 1):
                    items[clave] += 1
                else:
                    messages.error(request, "No hay más stock de %s." % producto.nombre)
            elif accion == "restar":
                if items[clave] - 1 < producto.minimo_compra:
                    items.pop(clave, None)
                    messages.info(
                        request,
                        "%s se quitó del carrito (compra mínima: %s)."
                        % (producto.nombre, producto.minimo_compra),
                    )
                else:
                    items[clave] -= 1
        carrito["items"] = items
        request.session[CARRITO_TIENDA_SESSION_KEY] = carrito
        return redirect("portal_tienda_carrito")

    lineas = []
    total = 0
    for producto_id, cantidad in items.items():
        producto = productos.get(int(producto_id))
        if producto is None:
            continue
        subtotal = producto.precio * cantidad
        total += subtotal
        lineas.append(
            {"producto": producto, "cantidad": cantidad, "subtotal": subtotal}
        )

    return render(request, "tienda/carrito.html", {"lineas": lineas, "total": total})


@tienda_required
def tienda_entrega(request):
    carrito = _carrito_tienda(request)
    items = carrito.get("items", {})
    mayorista = Mayorista.objects.filter(pk=carrito.get("mayorista_id")).first()

    if not items or mayorista is None:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("portal_tienda_marketplace")

    productos = {p.id: p for p in Producto.objects.filter(pk__in=items.keys())}
    lineas = [
        {"producto": productos[int(pid)], "cantidad": cantidad}
        for pid, cantidad in items.items()
        if int(pid) in productos
    ]
    total = sum((linea["producto"].precio * linea["cantidad"] for linea in lineas), 0)

    if request.method == "POST":
        formulario = PedidoEntregaForm(request.POST)
        if formulario.is_valid():
            try:
                pedido = Pedido.crear_validado(
                    tienda=request.tienda,
                    mayorista=mayorista,
                    vendedor=None,
                    creado_por="tienda",
                    tipo_pago=formulario.cleaned_data["tipo_pago"],
                    lineas=lineas,
                    telefono_contacto=formulario.cleaned_data["telefono_contacto"],
                    nota_voz=formulario.cleaned_data.get("nota_voz") or None,
                    lat=formulario.cleaned_data["lat"],
                    lng=formulario.cleaned_data["lng"],
                )
            except ValueError as error:
                messages.error(request, str(error))
                return redirect("portal_tienda_entrega")

            request.session.pop(CARRITO_TIENDA_SESSION_KEY, None)
            return redirect("portal_tienda_confirmacion", pedido_id=pedido.id)
    else:
        formulario = PedidoEntregaForm(
            initial={
                "telefono_contacto": request.tienda.telefono or "",
                "lat": request.tienda.lat,
                "lng": request.tienda.lng,
            }
        )

    return render(
        request,
        "tienda/entrega.html",
        {
            "formulario": formulario,
            "mayorista": mayorista,
            "lineas": lineas,
            "total": total,
        },
    )


@tienda_required
def tienda_confirmacion(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, tienda=request.tienda)
    return render(request, "tienda/confirmacion.html", {"pedido": pedido})


@tienda_required
def tienda_mis_pedidos(request):
    filtro = request.GET.get("filtro", "todos")

    pedidos = (
        Pedido.objects.filter(tienda=request.tienda)
        .select_related("mayorista")
        .prefetch_related("items__producto")
        .order_by("-creado_en")
    )

    if filtro == "en_curso":
        pedidos = pedidos.filter(estado__in=["pendiente", "validado", "en_camino"])
    elif filtro == "entregados":
        pedidos = pedidos.filter(estado="entregado")

    return render(
        request,
        "tienda/mis_pedidos.html",
        {
            "pedidos": pedidos,
            "filtro": filtro,
        },
    )


# ===================== Administrador =====================


@admin_required
def admin_dashboard(request):
    contexto = Mayorista.obtener_resumen_administracion()

    return render(
        request,
        "admin/dashboard.html",
        contexto,
    )


@admin_required
def admin_mayoristas(request):
    estado = request.GET.get("estado", "")

    mayoristas = Mayorista.objects.select_related("cuenta").order_by("-id")
    if estado:
        mayoristas = mayoristas.filter(estado=estado)

    return render(
        request,
        "admin/mayoristas.html",
        {
            "mayoristas": mayoristas,
            "estado": estado,
            "pendientes": Mayorista.objects.filter(estado="pendiente_pago").count(),
        },
    )


@admin_required
def admin_mayorista_toggle(request, id):
    mayorista = get_object_or_404(Mayorista, pk=id)

    # Una cuenta pendiente no puede activarse sin configuración comercial
    if mayorista.estado == "pendiente_pago":
        messages.warning(
            request,
            "Primero debes asignar un plan y configurar las condiciones "
            f"comerciales de {mayorista.nombre}.",
        )
        return redirect("portal_admin_mayorista_configuracion", id=mayorista.id)

    # Solo permite suspender o reactivar cuentas ya configuradas
    if mayorista.estado == "activo":
        mayorista.estado = "suspendido"
        mensaje = f"{mayorista.nombre} ha sido suspendido."
    else:
        mayorista.estado = "activo"
        mensaje = f"{mayorista.nombre} ha sido reactivado."

    mayorista.save(update_fields=["estado"])
    messages.success(request, mensaje)

    return redirect("portal_admin_mayoristas")


@admin_required
def admin_mayorista_configuracion(request, id):
    mayorista = get_object_or_404(
        Mayorista.objects.select_related("cuenta"),
        pk=id,
    )

    estaba_pendiente = mayorista.estado == "pendiente_pago"

    if request.method == "POST":
        formulario = MayoristaConfigComercialForm(
            request.POST,
            instance=mayorista,
        )

        if formulario.is_valid():
            mayorista_configurado = formulario.save(commit=False)

            if estaba_pendiente:
                mayorista_configurado.estado = "activo"

            mayorista_configurado.save()

            if estaba_pendiente:
                messages.success(
                    request,
                    "%s fue configurado y activado correctamente."
                    % mayorista_configurado.nombre,
                )
            else:
                messages.success(
                    request,
                    "Las condiciones comerciales de %s "
                    "fueron actualizadas." % mayorista_configurado.nombre,
                )

            return redirect("portal_admin_mayoristas")
    else:
        formulario = MayoristaConfigComercialForm(instance=mayorista)

    return render(
        request,
        "admin/mayorista_configuracion.html",
        {
            "formulario": formulario,
            "mayorista": mayorista,
            "activar_al_guardar": estaba_pendiente,
        },
    )


@admin_required
def admin_configuracion(request):
    filtro = request.GET.get("filtro", "todos")
    busqueda = request.GET.get("q", "").strip()

    mayoristas = Mayorista.objects.select_related("cuenta").order_by("nombre")

    # Los filtros corresponden únicamente al tipo de acuerdo comercial
    filtros_permitidos = {
        "sin_asignar",
        "comision",
        "suscripcion",
        "mixto",
    }

    if filtro in filtros_permitidos:
        mayoristas = mayoristas.filter(plan=filtro)
    else:
        filtro = "todos"

    # En Configuración solamente necesitamos buscar por empresa
    if busqueda:
        mayoristas = mayoristas.filter(nombre__icontains=busqueda)

    contexto = {
        "mayoristas": mayoristas,
        "filtro": filtro,
        "busqueda": busqueda,
    }

    return render(
        request,
        "admin/configuracion.html",
        contexto,
    )


@admin_required
def admin_suscripciones(request):
    hoy = timezone.localdate()
    limite_por_vencer = hoy + timedelta(days=30)

    filtro = request.GET.get("filtro", "todas")

    filtros_permitidos = {
        "todas",
        "vigentes",
        "por_vencer",
        "vencidas",
    }

    if filtro not in filtros_permitidos:
        filtro = "todas"

    # Suscripciones solamente administra planes que tienen tarifa anual
    suscripciones_base = (
        Mayorista.objects
        .filter(plan__in=["suscripcion", "mixto"])
        .select_related("cuenta")
    )

    # Total anual contratado por mayoristas activos
    ingresos_anuales = (
        suscripciones_base
        .filter(estado="activo")
        .aggregate(total=Sum("tarifa_anual"))["total"]
        or 0
    )

    # Cantidades utilizadas como alertas de renovación
    cantidad_por_vencer = suscripciones_base.filter(
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=limite_por_vencer,
    ).count()

    cantidad_vencidas = suscripciones_base.filter(
        fecha_vencimiento__lt=hoy
    ).count()

    # Filtros relacionados exclusivamente con el vencimiento
    if filtro == "vigentes":
        suscripciones = suscripciones_base.filter(
            fecha_vencimiento__gt=limite_por_vencer
        )

    elif filtro == "por_vencer":
        suscripciones = suscripciones_base.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite_por_vencer,
        )

    elif filtro == "vencidas":
        suscripciones = suscripciones_base.filter(
            fecha_vencimiento__lt=hoy
        )

    else:
        suscripciones = suscripciones_base

    suscripciones = suscripciones.order_by(
        "fecha_vencimiento",
        "nombre",
    )

    contexto = {
        "suscripciones": suscripciones,
        "ingresos_anuales": ingresos_anuales,
        "cantidad_por_vencer": cantidad_por_vencer,
        "cantidad_vencidas": cantidad_vencidas,
        "filtro": filtro,
        "hoy": hoy,
    }

    return render(
        request,
        "admin/suscripciones.html",
        contexto,
    )


# ===================== API REST (Django REST Framework) =====================


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver o editar usuarios.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver o editar grupos.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class MayoristaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar mayoristas.
    """

    queryset = Mayorista.objects.all()
    serializer_class = MayoristaSerializer
    permission_classes = [permissions.IsAuthenticated]


class VendedorViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar vendedores.
    """

    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = [permissions.IsAuthenticated]


class TiendaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar tiendas.
    """

    queryset = Tienda.objects.all()
    serializer_class = TiendaSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar productos.
    """

    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PedidoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar pedidos.
    """

    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PedidoItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar ítems de pedido.
    """

    queryset = PedidoItem.objects.all()
    serializer_class = PedidoItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class PagoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar pagos.
    """

    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAuthenticated]


class RendicionViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar rendiciones.
    """

    queryset = Rendicion.objects.all()
    serializer_class = RendicionSerializer
    permission_classes = [permissions.IsAuthenticated]
