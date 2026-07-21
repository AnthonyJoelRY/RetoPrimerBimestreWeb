from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from appDjango.models import Pago, Pedido, Producto, Rendicion, Tienda
from appDjango.portal.decorators import vendedor_required
from appDjango.portal.services import crear_pedido_validado

CARRITO_SESSION_KEY = "vendedor_carrito"


def _productos_disponibles(vendedor):
    if vendedor.tipo_perfil == "especializado" and vendedor.producto_asignado_id:
        return Producto.objects.filter(pk=vendedor.producto_asignado_id, activo=True)
    return Producto.objects.filter(mayorista=vendedor.mayorista, activo=True)


@vendedor_required
def dashboard(request):
    vendedor = request.vendedor

    por_cobrar = Pago.objects.filter(
        pedido__vendedor=vendedor, metodo="efectivo", estado="pendiente"
    ).aggregate(total=Sum("monto"))["total"] or 0

    pedidos_activos = Pedido.objects.filter(vendedor=vendedor).exclude(estado__in=["entregado", "cancelado"]).count()

    return render(request, "portal/vendedor/dashboard.html", {
        "por_cobrar": por_cobrar,
        "pedidos_activos": pedidos_activos,
    })


@vendedor_required
def cambiar_password(request):
    if request.method == "POST":
        formulario = SetPasswordForm(user=request.user, data=request.POST)
        if formulario.is_valid():
            formulario.save()
            update_session_auth_hash(request, formulario.user)
            vendedor = request.user.perfil_vendedor
            vendedor.primer_login = False
            vendedor.save(update_fields=["primer_login"])
            messages.success(request, "Contraseña actualizada. Ya puedes usar la plataforma.")
            return redirect("portal_vendedor_dashboard")
    else:
        formulario = SetPasswordForm(user=request.user)

    return render(request, "portal/vendedor/cambiar_password.html", {"formulario": formulario})


@vendedor_required
def nuevo_pedido_paso1(request):
    request.session.pop(CARRITO_SESSION_KEY, None)
    busqueda = request.GET.get("q", "")
    tiendas = Tienda.objects.none()
    if busqueda:
        tiendas = Tienda.objects.filter(Q(nombre__icontains=busqueda) | Q(telefono__icontains=busqueda))

    return render(request, "portal/vendedor/pedido_paso1.html", {"busqueda": busqueda, "tiendas": tiendas})


@vendedor_required
def nuevo_pedido_paso2(request, tienda_id):
    tienda = get_object_or_404(Tienda, pk=tienda_id)
    productos = _productos_disponibles(request.vendedor)
    carrito = request.session.get(CARRITO_SESSION_KEY, {})

    if request.method == "POST":
        nuevo_carrito = {}
        for producto in productos:
            cantidad = int(request.POST.get("cantidad_%s" % producto.id, 0) or 0)
            if cantidad > 0:
                nuevo_carrito[str(producto.id)] = cantidad
        request.session[CARRITO_SESSION_KEY] = nuevo_carrito
        request.session["vendedor_tienda_id"] = tienda.id
        if not nuevo_carrito:
            messages.error(request, "Selecciona al menos un producto.")
            return redirect("portal_vendedor_pedido_paso2", tienda_id=tienda.id)
        return redirect("portal_vendedor_pedido_paso3")

    filas = [{"producto": producto, "cantidad": carrito.get(str(producto.id), 0)} for producto in productos]

    return render(request, "portal/vendedor/pedido_paso2.html", {
        "tienda": tienda,
        "filas": filas,
    })


@vendedor_required
def nuevo_pedido_paso3(request):
    tienda_id = request.session.get("vendedor_tienda_id")
    carrito = request.session.get(CARRITO_SESSION_KEY, {})
    tienda = get_object_or_404(Tienda, pk=tienda_id) if tienda_id else None

    if not tienda or not carrito:
        messages.error(request, "Selecciona una tienda y productos antes de continuar.")
        return redirect("portal_vendedor_pedido_paso1")

    productos = {p.id: p for p in Producto.objects.filter(pk__in=carrito.keys())}
    lineas = []
    total = Decimal("0.00")
    for producto_id, cantidad in carrito.items():
        producto = productos[int(producto_id)]
        subtotal = producto.precio * cantidad
        total += subtotal
        lineas.append({"producto": producto, "cantidad": cantidad, "subtotal": subtotal})

    if request.method == "POST":
        tipo_pago = request.POST.get("tipo_pago", "efectivo")

        try:
            pedido = crear_pedido_validado(
                tienda=tienda,
                mayorista=request.vendedor.mayorista,
                vendedor=request.vendedor,
                creado_por="vendedor",
                tipo_pago=tipo_pago,
                lineas=lineas,
                telefono_contacto=tienda.telefono or "",
            )
        except ValueError as error:
            messages.error(request, str(error))
            return redirect("portal_vendedor_pedido_paso3")

        request.session.pop(CARRITO_SESSION_KEY, None)
        request.session.pop("vendedor_tienda_id", None)
        messages.success(request, "Pedido #%s registrado correctamente." % pedido.id)
        return redirect("portal_vendedor_dashboard")

    return render(request, "portal/vendedor/pedido_paso3.html", {"tienda": tienda, "lineas": lineas, "total": total})


@vendedor_required
def cobros_pendientes(request):
    pagos = Pago.objects.filter(
        pedido__vendedor=request.vendedor, metodo="efectivo", estado="pendiente"
    ).select_related("pedido", "pedido__tienda")

    return render(request, "portal/vendedor/cobros.html", {"pagos": pagos})


@vendedor_required
def marcar_cobrado(request, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id, pedido__vendedor=request.vendedor)
    pago.estado = "confirmado"
    pago.save(update_fields=["estado"])
    pago.pedido.cobro_confirmado = True
    pago.pedido.save(update_fields=["cobro_confirmado"])
    messages.success(request, "Cobro registrado.")
    return redirect("portal_vendedor_cobros")


@vendedor_required
def rendicion_caja(request):
    vendedor = request.vendedor
    pagos_por_rendir = Pago.objects.filter(
        pedido__vendedor=vendedor, metodo="efectivo", estado="confirmado", rendicion__isnull=True
    ).select_related("pedido")

    if request.method == "POST":
        if not pagos_por_rendir.exists():
            messages.error(request, "No tienes cobros pendientes por rendir.")
            return redirect("portal_vendedor_rendicion")

        with transaction.atomic():
            total_cobrado = pagos_por_rendir.aggregate(total=Sum("monto"))["total"] or 0
            total_comision = sum((p.pedido.comision_plataforma for p in pagos_por_rendir), Decimal("0.00"))

            rendicion = Rendicion.objects.create(
                vendedor=vendedor,
                mayorista=vendedor.mayorista,
                total_cobrado=total_cobrado,
                total_comision=total_comision,
            )
            pagos_por_rendir.update(rendicion=rendicion)

        messages.success(request, "Rendición enviada al mayorista.")
        return redirect("portal_vendedor_dashboard")

    total = pagos_por_rendir.aggregate(total=Sum("monto"))["total"] or 0
    return render(request, "portal/vendedor/rendicion.html", {"pagos": pagos_por_rendir, "total": total})
