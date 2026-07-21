from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from appDjango.models import Mayorista, Pedido, PlataformaConfig
from appDjango.portal.decorators import admin_required
from appDjango.portal.forms import PlataformaConfigForm


@admin_required
def dashboard(request):
    hoy = timezone.now().date()

    pedidos_mes = Pedido.objects.filter(creado_en__year=hoy.year, creado_en__month=hoy.month).exclude(estado="cancelado")

    ingresos_suscripciones = Mayorista.objects.filter(estado="activo", plan__in=["suscripcion", "mixto"]).aggregate(
        total=Sum("tarifa_anual")
    )["total"] or 0
    ingresos_comisiones = pedidos_mes.filter(estado="entregado").aggregate(total=Sum("comision_plataforma"))["total"] or 0

    contexto = {
        "mayoristas_activos": Mayorista.objects.filter(estado="activo").count(),
        "pendientes_activacion": Mayorista.objects.filter(estado="pendiente_pago").count(),
        "pedidos_mes": pedidos_mes.count(),
        "ingresos_estimados": (ingresos_suscripciones / 12) + ingresos_comisiones,
    }

    return render(request, "portal/admin/dashboard.html", contexto)


@admin_required
def mayoristas_list(request):
    mayoristas = Mayorista.objects.order_by("-id")
    return render(request, "portal/admin/mayoristas.html", {"mayoristas": mayoristas})


@admin_required
def mayorista_toggle(request, id):
    mayorista = get_object_or_404(Mayorista, pk=id)
    mayorista.estado = "suspendido" if mayorista.estado == "activo" else "activo"
    mayorista.save(update_fields=["estado"])
    messages.success(request, "%s ahora está %s." % (mayorista.nombre, mayorista.get_estado_display().lower()))
    return redirect("portal_admin_mayoristas")


@admin_required
def configuracion(request):
    config = PlataformaConfig.obtener()

    if request.method == "POST":
        formulario = PlataformaConfigForm(request.POST, instance=config)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Configuración comercial actualizada.")
            return redirect("portal_admin_configuracion")
    else:
        formulario = PlataformaConfigForm(instance=config)

    return render(request, "portal/admin/configuracion.html", {"formulario": formulario})


@admin_required
def suscripciones(request):
    return render(request, "portal/admin/suscripciones.html")
