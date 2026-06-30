from decimal import Decimal

from django.conf import settings
from django.db import models


class Mayorista(models.Model):
    CATEGORIA_CHOICES = [
        ("bebidas", "Bebidas"),
        ("abarrotes", "Abarrotes"),
        ("lacteos", "Lácteos"),
        ("limpieza", "Limpieza"),
        ("otro", "Otro"),
    ]

    PLAN_CHOICES = [
        ("suscripcion", "Suscripción"),
        ("comision", "Comisión"),
        ("mixto", "Mixto"),
    ]

    ESTADO_CHOICES = [
        ("pendiente_pago", "Pendiente de pago"),
        ("activo", "Activo"),
        ("suspendido", "Suspendido"),
    ]

    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_mayorista",
    )

    nombre = models.CharField(max_length=255)

    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    logo_url = models.TextField(blank=True, null=True)

    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente_pago"
    )

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="suscripcion")

    tarifa_anual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    porcentaje_comision = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    fecha_vencimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (
            self.nombre,
            self.get_categoria_display(),
            self.get_estado_display(),
        )


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

    cobro_confirmado = models.BooleanField(default=False)

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

    def __str__(self):
        return "Pedido #%s - %s - %s - %s" % (
            self.id,
            self.tienda.nombre,
            self.mayorista.nombre,
            self.get_estado_display(),
        )

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

    def __str__(self):
        return "Rendición #%s - %s - %s - %s" % (
            self.id,
            self.vendedor.nombre,
            self.mayorista.nombre,
            self.get_estado_display(),
        )

    def calcular_total_neto(self):
        return self.total_cobrado - self.total_comision
