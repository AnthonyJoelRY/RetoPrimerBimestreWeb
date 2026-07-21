from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from appDjango.models import Mayorista, Pedido, Producto
from appDjango.portal.decorators import tienda_required
from appDjango.portal.forms import PedidoEntregaForm
from appDjango.portal.services import crear_pedido_validado

CARRITO_SESSION_KEY = "tienda_carrito"


def _carrito(request):
    return request.session.get(CARRITO_SESSION_KEY, {"mayorista_id": None, "items": {}})


@tienda_required
def marketplace(request):
    mayoristas = Mayorista.objects.filter(estado="activo").order_by("nombre")
    return render(request, "portal/tienda/marketplace.html", {"mayoristas": mayoristas})


@tienda_required
def catalogo(request, mayorista_id):
    mayorista = get_object_or_404(Mayorista, pk=mayorista_id, estado="activo")
    productos = Producto.objects.filter(mayorista=mayorista, activo=True).order_by("nombre")
    carrito = _carrito(request)
    en_este_carrito = carrito["items"] if carrito.get("mayorista_id") == mayorista.id else {}

    return render(request, "portal/tienda/catalogo.html", {
        "mayorista": mayorista,
        "productos": productos,
        "carrito": en_este_carrito,
    })


@tienda_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    cantidad = int(request.POST.get("cantidad", producto.minimo_compra) or producto.minimo_compra)

    carrito = _carrito(request)
    if carrito.get("mayorista_id") not in (None, producto.mayorista_id):
        carrito = {"mayorista_id": None, "items": {}}
        messages.info(request, "Se reinició tu carrito porque cambiaste de mayorista.")

    carrito["mayorista_id"] = producto.mayorista_id
    items = carrito.get("items", {})
    items[str(producto.id)] = items.get(str(producto.id), 0) + cantidad
    carrito["items"] = items
    request.session[CARRITO_SESSION_KEY] = carrito

    messages.success(request, "%s agregado al carrito." % producto.nombre)
    return redirect("portal_tienda_catalogo", mayorista_id=producto.mayorista_id)


@tienda_required
def carrito_ver(request):
    carrito = _carrito(request)
    items = carrito.get("items", {})

    if request.method == "POST":
        for clave in list(items.keys()):
            accion = request.POST.get("accion_%s" % clave)
            if accion == "quitar":
                items.pop(clave, None)
            elif accion == "sumar":
                items[clave] += 1
            elif accion == "restar":
                items[clave] = max(0, items[clave] - 1)
                if items[clave] == 0:
                    items.pop(clave, None)
        carrito["items"] = items
        request.session[CARRITO_SESSION_KEY] = carrito
        return redirect("portal_tienda_carrito")

    productos = {p.id: p for p in Producto.objects.filter(pk__in=items.keys())}
    lineas = []
    total = Decimal("0.00")
    for producto_id, cantidad in items.items():
        producto = productos.get(int(producto_id))
        if producto is None:
            continue
        subtotal = producto.precio * cantidad
        total += subtotal
        lineas.append({"producto": producto, "cantidad": cantidad, "subtotal": subtotal})

    return render(request, "portal/tienda/carrito.html", {"lineas": lineas, "total": total})


@tienda_required
def entrega(request):
    carrito = _carrito(request)
    items = carrito.get("items", {})
    mayorista = Mayorista.objects.filter(pk=carrito.get("mayorista_id")).first()

    if not items or mayorista is None:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("portal_tienda_marketplace")

    productos = {p.id: p for p in Producto.objects.filter(pk__in=items.keys())}
    lineas = [{"producto": productos[int(pid)], "cantidad": cantidad} for pid, cantidad in items.items() if int(pid) in productos]
    total = sum((linea["producto"].precio * linea["cantidad"] for linea in lineas), Decimal("0.00"))

    if request.method == "POST":
        formulario = PedidoEntregaForm(request.POST)
        if formulario.is_valid():
            try:
                pedido = crear_pedido_validado(
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

            request.session.pop(CARRITO_SESSION_KEY, None)
            return redirect("portal_tienda_confirmacion", pedido_id=pedido.id)
    else:
        formulario = PedidoEntregaForm(initial={
            "telefono_contacto": request.tienda.telefono or "",
            "lat": request.tienda.lat,
            "lng": request.tienda.lng,
        })

    return render(request, "portal/tienda/entrega.html", {
        "formulario": formulario,
        "mayorista": mayorista,
        "lineas": lineas,
        "total": total,
    })


@tienda_required
def confirmacion(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, tienda=request.tienda)
    return render(request, "portal/tienda/confirmacion.html", {"pedido": pedido})


@tienda_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(tienda=request.tienda).select_related("mayorista").order_by("-creado_en")
    return render(request, "portal/tienda/mis_pedidos.html", {"pedidos": pedidos})
