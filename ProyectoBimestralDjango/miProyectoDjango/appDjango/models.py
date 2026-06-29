from django.db import models

# Create your models here.
from django.db import models


# USUARIO (tabla padre - herencia por tabla)

class Usuario(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email


# MAYORISTA

CATEGORIA_CHOICES = [
    ('Bebidas', 'Bebidas'),
    ('Abarrotes', 'Abarrotes'),
    ('Lacteos', 'Lacteos'),
    ('Limpieza', 'Limpieza'),
    ('Otro', 'Otro'),
]

PLAN_CHOICES = [
    ('suscripcion', 'Suscripcion'),
    ('comision', 'Comision'),
    ('mixto', 'Mixto'),
]

ESTADO_MAYORISTA_CHOICES = [
    ('pendiente_pago', 'Pendiente de pago'),
    ('activo', 'Activo'),
    ('suspendido', 'Suspendido'),
]


class Mayorista(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, primary_key=True
    )
    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    logo_url = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20, choices=ESTADO_MAYORISTA_CHOICES, default='pendiente_pago'
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='suscripcion')
    tarifa_anual = models.FloatField(default=0.0)
    porcentaje_comision = models.FloatField(default=0.0)
    fecha_vencimiento = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# VENDEDOR

TIPO_PERFIL_CHOICES = [
    ('general', 'General'),
    ('especializado', 'Especializado'),
]


class Vendedor(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, primary_key=True
    )
    mayorista = models.ForeignKey(
        Mayorista, on_delete=models.CASCADE, related_name='vendedores'
    )
    nombre = models.CharField(max_length=255)
    primer_login = models.IntegerField(default=1)
    tipo_perfil = models.CharField(
        max_length=20, choices=TIPO_PERFIL_CHOICES, default='general'
    )
    producto_asignado = models.ForeignKey(
        'Producto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendedores_asignados',
    )
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.nombre


# TIENDA

class Tienda(models.Model):
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    logo = models.TextField(blank=True, null=True)
    password = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    direccion_texto = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# PRODUCTO

class Producto(models.Model):
    mayorista = models.ForeignKey(
        Mayorista, on_delete=models.CASCADE, related_name='productos'
    )
    nombre = models.CharField(max_length=255)
    foto_url = models.TextField()
    precio = models.FloatField()
    stock = models.IntegerField(default=0)
    minimo_compra = models.IntegerField(default=1)
    unidad = models.CharField(max_length=50)
    activo = models.IntegerField(default=1)

    def __str__(self):
        return "%s – %s" % (self.nombre, self.mayorista.nombre)

    def verificar_stock(self, cantidad):
        return self.stock >= cantidad

    def descontar_stock(self, cantidad):
        self.stock -= cantidad
        self.save()


# PEDIDO

ESTADO_PEDIDO_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('validado', 'Validado'),
    ('en_camino', 'En camino'),
    ('entregado', 'Entregado'),
    ('cancelado', 'Cancelado'),
]

TIPO_PAGO_CHOICES = [
    ('efectivo', 'Efectivo'),
    ('tarjeta', 'Tarjeta'),
    ('transferencia', 'Transferencia'),
]

CREADO_POR_CHOICES = [
    ('tienda', 'Tienda'),
    ('vendedor', 'Vendedor'),
]


class Pedido(models.Model):
    tienda = models.ForeignKey(
        Tienda, on_delete=models.CASCADE, related_name='pedidos'
    )
    mayorista = models.ForeignKey(
        Mayorista, on_delete=models.CASCADE, related_name='pedidos', null=True, blank=True
    )
    vendedor = models.ForeignKey(
        Vendedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos'
    )
    creado_por = models.CharField(max_length=10, choices=CREADO_POR_CHOICES)
    estado = models.CharField(
        max_length=20, choices=ESTADO_PEDIDO_CHOICES, default='pendiente'
    )
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES)
    total = models.FloatField(default=0.0)
    comision_plataforma = models.FloatField(default=0.0)
    cobro_confirmado = models.IntegerField(default=0)
    nota_voz_url = models.TextField(blank=True, null=True)
    lat_entrega = models.FloatField(blank=True, null=True)
    lng_entrega = models.FloatField(blank=True, null=True)
    telefono_contacto = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Pedido #%s – %s" % (self.id, self.tienda.nombre)


# PEDIDO ITEM

class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='items'
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name='pedido_items'
    )
    cantidad = models.IntegerField()
    precio_unitario = models.FloatField()
    subtotal = models.FloatField()

    class Meta:
        unique_together = ('pedido', 'producto')

    def __str__(self):
        return "%s x%s" % (self.producto.nombre, self.cantidad)

    def calcular_subtotal(self):
        self.subtotal = self.cantidad * self.precio_unitario
        return self.subtotal


# PAGO

METODO_PAGO_CHOICES = [
    ('efectivo', 'Efectivo'),
    ('tarjeta', 'Tarjeta'),
    ('transferencia', 'Transferencia'),
]

ESTADO_PAGO_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('confirmado', 'Confirmado'),
    ('rechazado', 'Rechazado'),
]


class Pago(models.Model):
    pedido = models.OneToOneField(
        Pedido, on_delete=models.CASCADE, related_name='pago'
    )
    metodo = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    monto = models.FloatField()
    estado = models.CharField(
        max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente'
    )

    def __str__(self):
        return "Pago #%s – %s – %s" % (self.id, self.metodo, self.estado)


# RENDICION

ESTADO_RENDICION_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('confirmado', 'Confirmado'),
]


class Rendicion(models.Model):
    vendedor = models.ForeignKey(
        Vendedor, on_delete=models.CASCADE, related_name='rendiciones'
    )
    mayorista = models.ForeignKey(
        Mayorista, on_delete=models.CASCADE, related_name='rendiciones'
    )
    total_cobrado = models.FloatField(default=0.0)
    total_comision = models.FloatField(default=0.0)
    estado = models.CharField(
        max_length=20, choices=ESTADO_RENDICION_CHOICES, default='pendiente'
    )

    def __str__(self):
        return "Rendicion #%s – %s" % (self.id, self.vendedor.nombre)