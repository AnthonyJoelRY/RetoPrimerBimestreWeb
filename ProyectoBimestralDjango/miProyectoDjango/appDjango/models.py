from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Mayorista(models.Model):
    CATEGORIA_CHOICES = [
        ("bebidas", "Bebidas"),
        ("abarrotes", "Abarrotes"),
        ("lacteos", "Lácteos"),
        ("limpieza", "Limpieza"),
        ("otro", "Otro"),
    ]

    PLAN_CHOICES = [
        ("sin_asignar", "Sin asignar"),
        ("suscripcion", "Suscripción anual"),
        ("comision", "Solo comisión"),
        ("mixto", "Mixto"),
    ]

    ESTADO_CHOICES = [
        ("pendiente_pago", "Pendiente de pago"),
        ("activo", "Activo"),
        ("suspendido", "Suspendido"),
    ]

    MESES_CORTOS = [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic",
    ]

    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_mayorista",
    )

    nombre = models.CharField(max_length=255)

    telefono = models.CharField(
        max_length=15,
        default="",
    )

    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    logo_url = models.TextField(blank=True, null=True)

    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente_pago"
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="sin_asignar",
    )

    tarifa_anual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    porcentaje_comision = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    fecha_vencimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (
            self.nombre,
            self.get_categoria_display(),
            self.get_estado_display(),
        )

    @property
    def estado_comercial(self):
        if not self.plan or self.plan == "sin_asignar":
            return "sin_configurar"

        # Los planes de suscripción y mixto necesitan vencimiento
        if self.plan in ("suscripcion", "mixto"):
            if not self.fecha_vencimiento:
                return "sin_configurar"

            hoy = timezone.localdate()

            if self.fecha_vencimiento < hoy:
                return "vencido"

            limite_por_vencer = hoy + timedelta(days=30)

            if self.fecha_vencimiento <= limite_por_vencer:
                return "por_vencer"

        return "vigente"
    
    @property
    def dias_para_vencimiento(self):
        if not self.fecha_vencimiento:
            return None

        hoy = timezone.localdate()

        return (self.fecha_vencimiento - hoy).days

    def obtener_resumen_dashboard(self, fecha=None):
        fecha = fecha or timezone.localdate()
        pedidos = self.pedidos.all()

        pedidos_hoy = pedidos.filter(
            creado_en__date=fecha,
            estado="pendiente",
        ).count()

        ventas_mes = pedidos.filter(
            creado_en__year=fecha.year,
            creado_en__month=fecha.month,
        ).exclude(estado="cancelado").aggregate(total=models.Sum("total"))[
            "total"
        ] or Decimal(
            "0.00"
        )

        stock_critico = self.productos.filter(
            activo=True,
            stock__lt=10,
        ).count()

        rendiciones_pendientes = self.rendiciones.filter(
            estado="pendiente",
        ).count()

        ultimos_pedidos = pedidos.select_related("tienda").order_by("-creado_en")[:5]

        return {
            "pedidos_hoy": pedidos_hoy,
            "ventas_mes": ventas_mes,
            "stock_critico": stock_critico,
            "rendiciones_pendientes": rendiciones_pendientes,
            "ultimos_pedidos": ultimos_pedidos,
        }

    @classmethod
    def obtener_resumen_administracion(cls):
        hoy = timezone.localdate()
        limite_renovacion = hoy + timedelta(days=30)

        # Todos los pedidos registrados durante el mes actual
        pedidos_registrados = Pedido.objects.filter(
            creado_en__year=hoy.year,
            creado_en__month=hoy.month,
        )

        # Los cancelados no forman parte de las ventas
        pedidos_validos = pedidos_registrados.exclude(
            estado="cancelado"
        )

        cantidad_pedidos_validos = pedidos_validos.count()

        pedidos_en_proceso = pedidos_registrados.filter(
            estado__in=[
                "pendiente",
                "validado",
                "en_camino",
            ]
        ).count()

        pedidos_entregados = pedidos_registrados.filter(
            estado="entregado"
        ).count()

        pedidos_cancelados = pedidos_registrados.filter(
            estado="cancelado"
        ).count()

        # Total vendido mediante pedidos no cancelados
        ventas_mes = (
            pedidos_validos.aggregate(
                total=models.Sum("total")
            )["total"]
            or Decimal("0.00")
        )

        # Promedio de dinero por cada pedido no cancelado
        if cantidad_pedidos_validos > 0:
            ticket_promedio = (
                ventas_mes / Decimal(cantidad_pedidos_validos)
            )
        else:
            ticket_promedio = Decimal("0.00")

        # Porcentaje de pedidos no cancelados que fueron entregados
        if cantidad_pedidos_validos > 0:
            tasa_entrega = (
                Decimal(pedidos_entregados)
                / Decimal(cantidad_pedidos_validos)
            ) * Decimal("100.00")
        else:
            tasa_entrega = Decimal("0.00")

        # Ingreso mensual estimado por suscripciones
        ingresos_suscripciones_anuales = (
            cls.objects.filter(
                estado="activo",
                plan__in=["suscripcion", "mixto"],
            ).aggregate(
                total=models.Sum("tarifa_anual")
            )["total"]
            or Decimal("0.00")
        )

        ingresos_suscripciones_mes = (
            ingresos_suscripciones_anuales
            / Decimal("12.00")
        )

        # Comisiones únicamente de pedidos entregados
        ingresos_comisiones_mes = (
            pedidos_registrados.filter(
                estado="entregado"
            ).aggregate(
                total=models.Sum("comision_plataforma")
            )["total"]
            or Decimal("0.00")
        )

        ingresos_plataforma = (
            ingresos_suscripciones_mes
            + ingresos_comisiones_mes
        )

        # Alertas de renovación
        suscripciones = cls.objects.filter(
            plan__in=["suscripcion", "mixto"],
            fecha_vencimiento__isnull=False,
        )

        suscripciones_por_vencer = suscripciones.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite_renovacion,
        ).count()

        suscripciones_vencidas = suscripciones.filter(
            fecha_vencimiento__lt=hoy
        ).count()

        return {
            # Resumen de empresas
            "mayoristas_activos": cls.objects.filter(
                estado="activo"
            ).count(),

            "pendientes_activacion": cls.objects.filter(
                estado="pendiente_pago"
            ).count(),

            # Indicadores económicos
            "ventas_mes": ventas_mes,
            "ingresos_plataforma": ingresos_plataforma,
            "ticket_promedio": ticket_promedio,
            "tasa_entrega": tasa_entrega,

            # Resumen de pedidos
            "pedidos_total": pedidos_registrados.count(),
            "pedidos_en_proceso": pedidos_en_proceso,
            "pedidos_entregados": pedidos_entregados,
            "pedidos_cancelados": pedidos_cancelados,

            # Alertas de suscripciones
            "suscripciones_por_vencer": suscripciones_por_vencer,
            "suscripciones_vencidas": suscripciones_vencidas,
        }

    def obtener_reporte_comercial(self, fecha=None):
        fecha = fecha or timezone.localdate()

        pedidos_entregados = self.pedidos.filter(estado="entregado")

        producto_estrella = (
            PedidoItem.objects.filter(
                pedido__mayorista=self,
                pedido__estado="entregado",
            )
            .values("producto__nombre")
            .annotate(total_vendido=models.Sum("cantidad"))
            .order_by("-total_vendido")
            .first()
        )

        mejor_tienda = (
            pedidos_entregados.values("tienda__nombre")
            .annotate(total_comprado=models.Sum("total"))
            .order_by("-total_comprado")
            .first()
        )

        mejor_vendedor = (
            pedidos_entregados.exclude(vendedor__isnull=True)
            .values("vendedor__nombre")
            .annotate(total_vendido=models.Sum("total"))
            .order_by("-total_vendido")
            .first()
        )

        comisiones_pagadas = pedidos_entregados.aggregate(
            total=models.Sum("comision_plataforma")
        )["total"] or Decimal("0.00")

        ventas_por_mes = []

        for desplazamiento in range(5, -1, -1):
            indice_mes = fecha.month - 1 - desplazamiento

            anio = fecha.year + indice_mes // 12

            mes = indice_mes % 12 + 1

            total = pedidos_entregados.filter(
                creado_en__year=anio,
                creado_en__month=mes,
            ).aggregate(total=models.Sum("total"))["total"] or Decimal("0.00")

            ventas_por_mes.append(
                {
                    "etiqueta": "%s %d"
                    % (
                        self.MESES_CORTOS[mes - 1],
                        anio % 100,
                    ),
                    "total": float(total),
                    "actual": (anio == fecha.year and mes == fecha.month),
                }
            )

        maximo = (
            max(
                (registro["total"] for registro in ventas_por_mes),
                default=0,
            )
            or 1
        )

        return {
            "producto_estrella": producto_estrella,
            "mejor_tienda": mejor_tienda,
            "mejor_vendedor": mejor_vendedor,
            "comisiones_pagadas": comisiones_pagadas,
            "ventas_por_mes": ventas_por_mes,
            "maximo": maximo,
        }


class Vendedor(models.Model):
    TIPO_PERFIL_CHOICES = [
        ("general", "General"),
        ("especializado", "Especializado"),
    ]

    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_vendedor",
    )

    mayorista = models.ForeignKey(
        Mayorista, on_delete=models.CASCADE, related_name="vendedores"
    )

    nombre = models.CharField(max_length=255)

    primer_login = models.BooleanField(default=True)

    tipo_perfil = models.CharField(
        max_length=20, choices=TIPO_PERFIL_CHOICES, default="general"
    )

    producto_asignado = models.ForeignKey(
        "Producto",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="vendedores_asignados",
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return "%s - %s - %s" % (
            self.nombre,
            self.mayorista.nombre,
            self.get_tipo_perfil_display(),
        )

    def obtener_productos_disponibles(self):
        if self.tipo_perfil == "especializado" and self.producto_asignado_id:
            return Producto.objects.filter(
                pk=self.producto_asignado_id,
                mayorista=self.mayorista,
                activo=True,
            )

        return self.mayorista.productos.filter(activo=True)

    def obtener_resumen_dashboard(self, fecha=None):
        fecha = fecha or timezone.localdate()

        pedidos = self.pedidos.all()

        pagos_efectivo = Pago.objects.filter(
            pedido__vendedor=self,
            metodo="efectivo",
        )

        por_cobrar = pagos_efectivo.filter(
            estado="pendiente",
        ).aggregate(
            total=models.Sum("monto")
        )["total"] or Decimal("0.00")

        por_rendir = pagos_efectivo.filter(
            estado="confirmado",
            rendicion__isnull=True,
        ).aggregate(total=models.Sum("monto"))["total"] or Decimal("0.00")

        pedidos_activos = pedidos.exclude(
            estado__in=[
                "entregado",
                "cancelado",
            ]
        ).count()

        ventas_hoy = pedidos.filter(
            creado_en__date=fecha,
        ).exclude(
            estado="cancelado"
        ).aggregate(total=models.Sum("total"))["total"] or Decimal("0.00")

        return {
            "por_cobrar": por_cobrar,
            "por_rendir": por_rendir,
            "pedidos_activos": pedidos_activos,
            "ventas_hoy": ventas_hoy,
        }


class Tienda(models.Model):
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil_tienda"
    )

    nombre = models.CharField(max_length=255)

    telefono = models.CharField(max_length=20, unique=True, blank=True, null=True)

    lat = models.FloatField(blank=True, null=True)

    lng = models.FloatField(blank=True, null=True)

    direccion_texto = models.TextField(blank=True, null=True)

    def __str__(self):
        identificador = self.cuenta.email or self.telefono or self.cuenta.username

        return "%s - %s" % (self.nombre, identificador)


class Producto(models.Model):
    UNIDAD_CHOICES = [
        ("unidad", "Unidad"),
        ("caja", "Caja"),
        ("kg", "Kilogramo"),
    ]

    mayorista = models.ForeignKey(
        Mayorista, on_delete=models.CASCADE, related_name="productos"
    )

    nombre = models.CharField(max_length=255)

    foto_url = models.TextField()

    precio = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)

    minimo_compra = models.PositiveIntegerField(default=1)

    unidad = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default="unidad")

    activo = models.BooleanField(default=True)

    def __str__(self):
        return "%s - %s - $%s" % (self.nombre, self.mayorista.nombre, self.precio)

    def verificar_stock(self, cantidad):
        return cantidad > 0 and cantidad <= self.stock

    def verificar_minimo_compra(self, cantidad):
        return cantidad > 0 and cantidad >= self.minimo_compra

    def descontar_stock(self, cantidad):
        self.stock = models.F("stock") - cantidad
        self.save(update_fields=["stock"])
        self.refresh_from_db(fields=["stock"])


class Pedido(models.Model):
    CREADO_POR_CHOICES = [
        ("tienda", "Tienda"),
        ("vendedor", "Vendedor"),
    ]

    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("validado", "Validado"),
        ("en_camino", "En camino"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]

    TIPO_PAGO_CHOICES = [
        ("efectivo", "Efectivo"),
        ("digital", "Digital"),
    ]

    tienda = models.ForeignKey(
        Tienda,
        on_delete=models.CASCADE,
        related_name="pedidos",
    )

    mayorista = models.ForeignKey(
        Mayorista,
        on_delete=models.CASCADE,
        related_name="pedidos",
    )

    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pedidos",
    )

    creado_por = models.CharField(
        max_length=10,
        choices=CREADO_POR_CHOICES,
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="pendiente",
    )

    tipo_pago = models.CharField(
        max_length=20,
        choices=TIPO_PAGO_CHOICES,
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
    )

    comision_plataforma = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
    )

    cobro_confirmado = models.BooleanField(
        default=False,
    )

    nota_voz_url = models.TextField(
        blank=True,
        null=True,
    )

    lat_entrega = models.FloatField(
        blank=True,
        null=True,
    )

    lng_entrega = models.FloatField(
        blank=True,
        null=True,
    )

    telefono_contacto = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        null=True,
    )

    def __str__(self):
        return "Pedido #%s - %s - %s - %s" % (
            self.id,
            self.tienda.nombre,
            self.mayorista.nombre,
            self.get_estado_display(),
        )

    @classmethod
    def crear_validado(
        cls,
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

        with transaction.atomic():
            productos_bloqueados = {}

            # Se bloquean y validan los productos antes de crear el pedido.
            for linea in lineas:
                producto = Producto.objects.select_for_update().get(
                    pk=linea["producto"].id
                )

                cantidad = linea["cantidad"]

                if not producto.verificar_stock(cantidad):
                    raise ValueError("No hay stock suficiente de %s." % producto.nombre)

                if not producto.verificar_minimo_compra(cantidad):
                    raise ValueError(
                        "%s requiere un mínimo de %s unidades por pedido."
                        % (
                            producto.nombre,
                            producto.minimo_compra,
                        )
                    )

                productos_bloqueados[producto.id] = producto

            # Se crea el pedido después de validar todos los productos.
            pedido = cls.objects.create(
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

            # Se crean los detalles y se descuenta el inventario.
            for linea in lineas:
                producto = productos_bloqueados[linea["producto"].id]

                cantidad = linea["cantidad"]

                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                )

                producto.descontar_stock(cantidad)

            # Se calculan el total y la comisión.
            pedido.actualizar_totales()

            es_digital = tipo_pago == "digital"

            # Se registra el pago relacionado con el pedido.
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

    def aplicar_transicion(self, accion):

        with transaction.atomic():
            pedido = type(self).objects.select_for_update().get(pk=self.pk)

            if accion == "enviar_ruta" and pedido.estado == "validado":
                pedido.estado = "en_camino"

            elif accion == "marcar_entregado" and pedido.estado == "en_camino":
                pedido.estado = "entregado"

            elif accion == "cancelar" and pedido.estado in ["pendiente", "validado"]:
                for item in pedido.items.all():
                    Producto.objects.filter(pk=item.producto_id).update(
                        stock=models.F("stock") + item.cantidad
                    )

                pedido.estado = "cancelado"

            else:
                raise ValueError(
                    "No se puede aplicar esa acción al pedido " "en su estado actual."
                )

            pedido.save(update_fields=["estado"])

        # Actualiza también el objeto que ya estaba cargado en la vista.
        self.estado = pedido.estado

        return self

    def calcular_total(self):
        total = Decimal("0.00")

        for item in self.items.all():
            total = total + item.calcular_subtotal()

        return total

    def calcular_comision(self):
        total = self.calcular_total()

        if self.mayorista.plan in ["comision", "mixto"]:
            return total * self.mayorista.porcentaje_comision / Decimal("100.00")

        return Decimal("0.00")

    def actualizar_totales(self):
        self.total = self.calcular_total()
        self.comision_plataforma = self.calcular_comision()

        self.save(
            update_fields=[
                "total",
                "comision_plataforma",
            ]
        )


class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="items",
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="pedido_items",
    )

    cantidad = models.PositiveIntegerField()

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
    )

    class Meta:
        unique_together = ("pedido", "producto")

    def __str__(self):
        return "%s - cantidad: %s - pedido: #%s" % (
            self.producto.nombre,
            self.cantidad,
            self.pedido.id,
        )

    def calcular_subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        self.subtotal = self.calcular_subtotal()
        super().save(*args, **kwargs)
        self.pedido.actualizar_totales()

    def delete(self, *args, **kwargs):
        pedido = self.pedido
        super().delete(*args, **kwargs)
        pedido.actualizar_totales()


class Pago(models.Model):
    METODO_CHOICES = [
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
    ]

    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("confirmado", "Confirmado"),
        ("rechazado", "Rechazado"),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="pago")

    metodo = models.CharField(max_length=20, choices=METODO_CHOICES)

    monto = models.DecimalField(max_digits=12, decimal_places=2)

    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente"
    )

    rendicion = models.ForeignKey(
        "Rendicion",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pagos",
    )

    def __str__(self):
        return "Pago pedido #%s - %s - $%s - %s" % (
            self.pedido.id,
            self.get_metodo_display(),
            self.monto,
            self.get_estado_display(),
        )

    def verificar_monto_correcto(self):
        return self.monto == self.pedido.calcular_total()


class Rendicion(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("confirmado", "Confirmado por mayorista"),
    ]

    vendedor = models.ForeignKey(
        Vendedor, on_delete=models.CASCADE, related_name="rendiciones"
    )

    mayorista = models.ForeignKey(
        Mayorista, on_delete=models.CASCADE, related_name="rendiciones"
    )

    total_cobrado = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total_comision = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente"
    )

    creado_en = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return "Rendición #%s - %s - %s - %s" % (
            self.id,
            self.vendedor.nombre,
            self.mayorista.nombre,
            self.get_estado_display(),
        )

    @classmethod
    def obtener_pagos_por_rendir(cls, vendedor):
        """
        Obtiene los pagos en efectivo confirmados que el vendedor
        todavía no ha incluido en una rendición.
        """
        return Pago.objects.filter(
            pedido__vendedor=vendedor,
            metodo="efectivo",
            estado="confirmado",
            rendicion__isnull=True,
        ).select_related("pedido")

    @classmethod
    def calcular_total_por_rendir(cls, vendedor):
        pagos = cls.obtener_pagos_por_rendir(vendedor)

        return pagos.aggregate(total=models.Sum("monto"))["total"] or Decimal("0.00")

    @classmethod
    def crear_para_vendedor(cls, vendedor):
        with transaction.atomic():
            pagos = (
                Pago.objects.select_for_update()
                .filter(
                    pedido__vendedor=vendedor,
                    metodo="efectivo",
                    estado="confirmado",
                    rendicion__isnull=True,
                )
                .select_related("pedido")
            )

            if not pagos.exists():
                raise ValueError("No tienes cobros pendientes por rendir.")

            totales = pagos.aggregate(
                total_cobrado=models.Sum("monto"),
                total_comision=models.Sum("pedido__comision_plataforma"),
            )

            rendicion = cls.objects.create(
                vendedor=vendedor,
                mayorista=vendedor.mayorista,
                total_cobrado=(totales["total_cobrado"] or Decimal("0.00")),
                total_comision=(totales["total_comision"] or Decimal("0.00")),
                estado="pendiente",
            )

            pagos.update(rendicion=rendicion)

        return rendicion

    def calcular_total_neto(self):
        return self.total_cobrado - self.total_comision


class PlataformaConfig(models.Model):
    """Configuración comercial global (planes y comisiones por defecto)."""

    tarifa_suscripcion_anual = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("1200.00")
    )

    porcentaje_comision_default = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("5.00")
    )

    tarifa_plan_mixto = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("600.00")
    )

    porcentaje_comision_mixto = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("2.00")
    )

    def __str__(self):
        return "Configuración comercial de la plataforma"

    @classmethod
    def obtener(cls):
        config, _ = cls.objects.get_or_create(pk=1)
        return config
