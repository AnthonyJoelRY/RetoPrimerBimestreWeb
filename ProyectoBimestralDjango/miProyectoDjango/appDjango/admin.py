from django.contrib import admin
from appDjango.models import (
    Mayorista,
    Vendedor,
    Tienda,
    Producto,
    Pedido,
    PedidoItem,
    Pago,
    Rendicion
)


class MayoristaAdmin(admin.ModelAdmin):
    list_display = (
        'cuenta',
        'nombre',
        'categoria',
        'estado',
        'plan',
        'tarifa_anual',
        'porcentaje_comision',
        'fecha_vencimiento'
    )

    search_fields = ('nombre','cuenta__username','cuenta__email')

    # Permite buscar y seleccionar la cuenta relacionada
    raw_id_fields = ('cuenta',)


admin.site.register(Mayorista, MayoristaAdmin)



class VendedorAdmin(admin.ModelAdmin):
    list_display = (
        'cuenta',
        'nombre',
        'mayorista',
        'tipo_perfil',
        'producto_asignado',
        'primer_login',
        'activo'
    )

    search_fields = ('nombre','cuenta__username','cuenta__email','mayorista__nombre','producto_asignado__nombre')
    raw_id_fields = ('cuenta','mayorista','producto_asignado')

admin.site.register(Vendedor, VendedorAdmin)



class TiendaAdmin(admin.ModelAdmin):
    list_display = (
        'cuenta',
        'nombre',
        'telefono',
        'lat',
        'lng',
        'direccion_texto'
    )

    search_fields = ('nombre','telefono','cuenta__username','cuenta__email','direccion_texto')
    raw_id_fields = ('cuenta',)


admin.site.register(Tienda, TiendaAdmin)



class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'mayorista',
        'precio',
        'stock',
        'minimo_compra',
        'unidad',
        'activo'
    )

    search_fields = ('nombre','mayorista__nombre')
    raw_id_fields = ('mayorista',)

admin.site.register(Producto, ProductoAdmin)


class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tienda',
        'mayorista',
        'vendedor',
        'creado_por',
        'estado',
        'tipo_pago',
        'total',
        'comision_plataforma',
        'cobro_confirmado'
    )

    search_fields = ('tienda__nombre','mayorista__nombre','vendedor__nombre','telefono_contacto')
    raw_id_fields = ('tienda','mayorista','vendedor')

admin.site.register(Pedido, PedidoAdmin)



class PedidoItemAdmin(admin.ModelAdmin):
    list_display = (
        'pedido',
        'producto',
        'cantidad',
        'precio_unitario',
        'subtotal'
    )

    search_fields = ('producto__nombre','pedido__tienda__nombre','pedido__mayorista__nombre')
    raw_id_fields = ('pedido','producto')

admin.site.register(PedidoItem, PedidoItemAdmin)



class PagoAdmin(admin.ModelAdmin):
    list_display = (
        'pedido',
        'metodo',
        'monto',
        'estado'
    )

    search_fields = ('pedido__tienda__nombre','pedido__mayorista__nombre')
    raw_id_fields = ('pedido',)

admin.site.register(Pago, PagoAdmin)




class RendicionAdmin(admin.ModelAdmin):
    list_display = (
        'vendedor',
        'mayorista',
        'total_cobrado',
        'total_comision',
        'estado'
    )

    search_fields = ('vendedor__nombre','mayorista__nombre')
    raw_id_fields = ('vendedor','mayorista')

admin.site.register(Rendicion, RendicionAdmin)