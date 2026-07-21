from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from appDjango.models import Pedido, PedidoItem, Producto, Rendicion, Vendedor
from appDjango.portal.decorators import mayorista_required
from appDjango.portal.forms import AjusteStockForm, ProductoMayoristaForm, VendedorCrearForm

STOCK_CRITICO = 10


@mayorista_required
def dashboard(request):
    mayorista = request.mayorista
    hoy = timezone.now().date()

    pedidos_qs = Pedido.objects.filter(mayorista=mayorista)

    contexto = {
        "pedidos_hoy": pedidos_qs.filter(creado_en__date=hoy, estado="pendiente").count(),
        "ventas_mes": pedidos_qs.filter(
            creado_en__year=hoy.year, creado_en__month=hoy.month
        ).exclude(estado="cancelado").aggregate(total=Sum("total"))["total"] or 0,
        "stock_critico": Producto.objects.filter(mayorista=mayorista, activo=True, stock__lt=STOCK_CRITICO).count(),
        "rendiciones_pendientes": Rendicion.objects.filter(mayorista=mayorista, estado="pendiente").count(),
    }

    return render(request, "portal/mayorista/dashboard.html", contexto)


@mayorista_required
def productos_list(request):
    productos = Producto.objects.filter(mayorista=request.mayorista).order_by("-id")
    return render(request, "portal/mayorista/productos.html", {"productos": productos})


@mayorista_required
def producto_crear(request):
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

    return render(request, "portal/mayorista/producto_form.html", {"formulario": formulario, "titulo": "Nuevo producto"})


@mayorista_required
def producto_editar(request, id):
    producto = get_object_or_404(Producto, pk=id, mayorista=request.mayorista)

    if request.method == "POST":
        formulario = ProductoMayoristaForm(request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto actualizado.")
            return redirect("portal_mayorista_productos")
    else:
        formulario = ProductoMayoristaForm(instance=producto)

    return render(request, "portal/mayorista/producto_form.html", {"formulario": formulario, "titulo": "Editar producto"})


@mayorista_required
def producto_eliminar(request, id):
    producto = get_object_or_404(Producto, pk=id, mayorista=request.mayorista)
    producto.delete()
    messages.success(request, "Producto eliminado.")
    return redirect("portal_mayorista_productos")


@mayorista_required
def inventario(request):
    if request.method == "POST":
        producto = get_object_or_404(Producto, pk=request.POST.get("producto_id"), mayorista=request.mayorista)
        formulario = AjusteStockForm(request.POST)
        if formulario.is_valid():
            producto.stock = formulario.cleaned_data["stock"]
            producto.save(update_fields=["stock"])
            messages.success(request, "Stock actualizado.")
        return redirect("portal_mayorista_inventario")

    productos = Producto.objects.filter(mayorista=request.mayorista).order_by("nombre")
    return render(request, "portal/mayorista/inventario.html", {"productos": productos, "stock_critico": STOCK_CRITICO})


@mayorista_required
def pedidos_list(request):
    estado = request.GET.get("estado", "")
    pedidos = Pedido.objects.filter(mayorista=request.mayorista).select_related("tienda", "vendedor").order_by("-creado_en")
    if estado:
        pedidos = pedidos.filter(estado=estado)

    return render(request, "portal/mayorista/pedidos.html", {
        "pedidos": pedidos,
        "estado_seleccionado": estado,
        "estados": Pedido.ESTADO_CHOICES,
    })


@mayorista_required
def pedido_transicion(request, id, accion):
    pedido = get_object_or_404(Pedido, pk=id, mayorista=request.mayorista)

    with transaction.atomic():
        if accion == "enviar_ruta" and pedido.estado == "validado":
            pedido.estado = "en_camino"
            pedido.save(update_fields=["estado"])
        elif accion == "marcar_entregado" and pedido.estado == "en_camino":
            pedido.estado = "entregado"
            pedido.save(update_fields=["estado"])
        elif accion == "cancelar" and pedido.estado in ("pendiente", "validado"):
            for item in pedido.items.select_related("producto"):
                item.producto.stock = item.producto.stock + item.cantidad
                item.producto.save(update_fields=["stock"])
            pedido.estado = "cancelado"
            pedido.save(update_fields=["estado"])
        else:
            messages.error(request, "No se puede aplicar esa acción al pedido en su estado actual.")
            return redirect("portal_mayorista_pedidos")

    messages.success(request, "Pedido #%s actualizado." % pedido.id)
    return redirect("portal_mayorista_pedidos")


@mayorista_required
def vendedores_list(request):
    vendedores = Vendedor.objects.filter(mayorista=request.mayorista).order_by("nombre")
    return render(request, "portal/mayorista/vendedores.html", {"vendedores": vendedores})


@mayorista_required
def vendedor_crear(request):
    if request.method == "POST":
        formulario = VendedorCrearForm(request.POST, mayorista=request.mayorista)
        if formulario.is_valid():
            formulario.guardar()
            messages.success(
                request,
                "Vendedor creado. Contraseña inicial: %s (se le pedirá cambiarla al ingresar)." % VendedorCrearForm.CONTRASENA_INICIAL,
            )
            return redirect("portal_mayorista_vendedores")
    else:
        formulario = VendedorCrearForm(mayorista=request.mayorista)

    return render(request, "portal/mayorista/vendedor_form.html", {"formulario": formulario})


@mayorista_required
def vendedor_toggle(request, id):
    vendedor = get_object_or_404(Vendedor, pk=id, mayorista=request.mayorista)
    vendedor.activo = not vendedor.activo
    vendedor.save(update_fields=["activo"])
    return redirect("portal_mayorista_vendedores")


@mayorista_required
def rendiciones_list(request):
    rendiciones = Rendicion.objects.filter(mayorista=request.mayorista).order_by("-id")
    return render(request, "portal/mayorista/rendiciones.html", {"rendiciones": rendiciones})


@mayorista_required
def rendicion_confirmar(request, id):
    rendicion = get_object_or_404(Rendicion, pk=id, mayorista=request.mayorista)
    rendicion.estado = "confirmado"
    rendicion.save(update_fields=["estado"])
    messages.success(request, "Rendición confirmada.")
    return redirect("portal_mayorista_rendiciones")


@mayorista_required
def reportes(request):
    mayorista = request.mayorista
    pedidos_entregados = Pedido.objects.filter(mayorista=mayorista, estado="entregado")

    producto_estrella = (
        PedidoItem.objects.filter(pedido__mayorista=mayorista, pedido__estado="entregado")
        .values("producto__nombre")
        .annotate(total_vendido=Sum("cantidad"))
        .order_by("-total_vendido")
        .first()
    )

    mejor_tienda = (
        pedidos_entregados.values("tienda__nombre")
        .annotate(total_comprado=Sum("total"))
        .order_by("-total_comprado")
        .first()
    )

    mejor_vendedor = (
        pedidos_entregados.exclude(vendedor__isnull=True)
        .values("vendedor__nombre")
        .annotate(total_vendido=Sum("total"))
        .order_by("-total_vendido")
        .first()
    )

    comisiones_pagadas = pedidos_entregados.aggregate(total=Sum("comision_plataforma"))["total"] or 0

    hoy = timezone.now().date()
    ventas_por_mes = []
    for i in range(5, -1, -1):
        indice_mes = hoy.month - 1 - i
        anio = hoy.year + indice_mes // 12
        mes = indice_mes % 12 + 1
        total = pedidos_entregados.filter(creado_en__year=anio, creado_en__month=mes).aggregate(total=Sum("total"))["total"] or 0
        ventas_por_mes.append({"etiqueta": "%04d-%02d" % (anio, mes), "total": float(total)})

    maximo = max((m["total"] for m in ventas_por_mes), default=0) or 1

    return render(request, "portal/mayorista/reportes.html", {
        "producto_estrella": producto_estrella,
        "mejor_tienda": mejor_tienda,
        "mejor_vendedor": mejor_vendedor,
        "comisiones_pagadas": comisiones_pagadas,
        "ventas_por_mes": ventas_por_mes,
        "maximo": maximo,
    })


@mayorista_required
def mi_cuenta(request):
    if request.method == "POST":
        formulario = PasswordChangeForm(user=request.user, data=request.POST)
        if formulario.is_valid():
            formulario.save()
            update_session_auth_hash(request, formulario.user)
            messages.success(request, "Contraseña actualizada.")
            return redirect("portal_mayorista_mi_cuenta")
    else:
        formulario = PasswordChangeForm(user=request.user)

    return render(request, "portal/mayorista/mi_cuenta.html", {"formulario": formulario, "mayorista": request.mayorista})
