from django.db import transaction

from appDjango.models import Pago, Pedido, PedidoItem, Producto


def crear_pedido_validado(
    *,
    tienda,
    mayorista,
    vendedor,
    creado_por,
    tipo_pago,
    lineas,
    telefono_contacto="",
    nota_voz=None,
    lat=None,
    lng=None,
):
    """Crea un pedido validando stock y mínimo de compra dentro de una transacción atómica.

    `lineas` es una lista de dicts {"producto": Producto, "cantidad": int}.
    Lanza ValueError si el monto o el stock no son válidos (RF-08 / RF-10).
    """
    with transaction.atomic():
        productos_bloqueados = {}
        for linea in lineas:
            producto = Producto.objects.select_for_update().get(pk=linea["producto"].id)
            if not producto.verificar_stock(linea["cantidad"]):
                raise ValueError("No hay stock suficiente de %s." % producto.nombre)
            if not producto.verificar_minimo_compra(linea["cantidad"]):
                raise ValueError(
                    "%s requiere un mínimo de %s unidades por pedido." % (producto.nombre, producto.minimo_compra)
                )
            productos_bloqueados[producto.id] = producto

        pedido = Pedido.objects.create(
            tienda=tienda,
            mayorista=mayorista,
            vendedor=vendedor,
            creado_por=creado_por,
            estado="validado",
            tipo_pago=tipo_pago,
            telefono_contacto=telefono_contacto,
            nota_voz_url=nota_voz,
            lat_entrega=lat,
            lng_entrega=lng,
        )

        for linea in lineas:
            producto = productos_bloqueados[linea["producto"].id]
            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=linea["cantidad"],
                precio_unitario=producto.precio,
            )
            producto.descontar_stock(linea["cantidad"])

        pedido.actualizar_totales()

        es_digital = tipo_pago == "digital"
        Pago.objects.create(
            pedido=pedido,
            metodo="tarjeta" if es_digital else "efectivo",
            monto=pedido.total,
            estado="confirmado" if es_digital else "pendiente",
        )
        if es_digital:
            pedido.cobro_confirmado = True
            pedido.save(update_fields=["cobro_confirmado"])

    return pedido
