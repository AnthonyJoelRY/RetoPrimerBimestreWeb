from django.contrib import admin
from .models import Usuario, Mayorista, Vendedor, Tienda, Producto, Pedido, PedidoItem, Pago, Rendicion

# Register your models here.

# USUARIO
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')
    search_fields = ('email',)

admin.site.register(Usuario, UsuarioAdmin)


# MAYORISTA
class MayoristaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'plan', 'estado', 'tarifa_anual', 'porcentaje_comision')
    search_fields = ('nombre',)

admin.site.register(Mayorista, MayoristaAdmin)


# VENDEDOR
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mayorista', 'tipo_perfil', 'activo')
    # raw_id_fields permite buscar y seleccionar el mayorista
    # y el producto asignado desde una interfaz de búsqueda
    raw_id_fields = ('mayorista', 'producto_asignado')
    search_fields = ('nombre',)

admin.site.register(Vendedor, VendedorAdmin)


# TIENDA
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono')
    search_fields = ('nombre', 'telefono')

admin.site.register(Tienda, TiendaAdmin)


# PRODUCTO
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mayorista', 'precio', 'stock', 'minimo_compra', 'unidad', 'activo')
    # raw_id_fields permite buscar y seleccionar el mayorista
    # desde una interfaz de búsqueda
    raw_id_fields = ('mayorista',)
    search_fields = ('nombre',)

admin.site.register(Producto, ProductoAdmin)


# PEDIDO ITEM (inline dentro de Pedido)
class PedidoItemInline(admin.TabularInline):
    # Los ítems del pedido se muestran embebidos
    # dentro del formulario del pedido
    model = PedidoItem
    extra = 0


# PEDIDO
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tienda', 'mayorista', 'vendedor', 'estado', 'tipo_pago', 'total', 'creado_por')
    # raw_id_fields permite buscar y seleccionar tienda,
    # mayorista y vendedor desde una interfaz de búsqueda
    raw_id_fields = ('tienda', 'mayorista', 'vendedor')
    search_fields = ('tienda__nombre',)
    # inlines muestra los ítems del pedido
    # dentro del mismo formulario del pedido
    inlines = [PedidoItemInline]

admin.site.register(Pedido, PedidoAdmin)


# PEDIDO ITEM
class PedidoItemAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    # raw_id_fields permite buscar y seleccionar el pedido
    # y el producto desde una interfaz de búsqueda
    raw_id_fields = ('pedido', 'producto')

admin.site.register(PedidoItem, PedidoItemAdmin)


# PAGO
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'metodo', 'monto', 'estado')
    # raw_id_fields permite buscar y seleccionar el pedido
    # desde una interfaz de búsqueda
    raw_id_fields = ('pedido',)

admin.site.register(Pago, PagoAdmin)


# RENDICION
class RendicionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendedor', 'mayorista', 'total_cobrado', 'total_comision', 'estado')
    # raw_id_fields permite buscar y seleccionar el vendedor
    # y el mayorista desde una interfaz de búsqueda
    raw_id_fields = ('vendedor', 'mayorista')
    search_fields = ('vendedor__nombre',)

admin.site.register(Rendicion, RendicionAdmin)