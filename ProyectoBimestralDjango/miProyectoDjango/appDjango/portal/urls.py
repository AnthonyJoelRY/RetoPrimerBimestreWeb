from django.urls import path

from appDjango.portal import views_auth, views_mayorista, views_vendedor, views_tienda, views_admin

urlpatterns = [
    # Landing / autenticación
    path("", views_auth.landing, name="portal_landing"),
    path("registro/mayorista/", views_auth.registro_mayorista, name="portal_registro_mayorista"),
    path("registro/tienda/", views_auth.registro_tienda, name="portal_registro_tienda"),
    path("login/mayorista/", views_auth.login_mayorista, name="portal_login_mayorista"),
    path("login/tienda/", views_auth.login_tienda, name="portal_login_tienda"),
    path("login/vendedor/", views_auth.login_vendedor, name="portal_login_vendedor"),
    path("login/admin/", views_auth.login_admin, name="portal_login_admin"),
    path("salir/", views_auth.logout_portal, name="portal_logout"),

    # Mayorista
    path("mayorista/dashboard/", views_mayorista.dashboard, name="portal_mayorista_dashboard"),
    path("mayorista/productos/", views_mayorista.productos_list, name="portal_mayorista_productos"),
    path("mayorista/productos/nuevo/", views_mayorista.producto_crear, name="portal_mayorista_producto_crear"),
    path("mayorista/productos/<int:id>/editar/", views_mayorista.producto_editar, name="portal_mayorista_producto_editar"),
    path("mayorista/productos/<int:id>/eliminar/", views_mayorista.producto_eliminar, name="portal_mayorista_producto_eliminar"),
    path("mayorista/inventario/", views_mayorista.inventario, name="portal_mayorista_inventario"),
    path("mayorista/pedidos/", views_mayorista.pedidos_list, name="portal_mayorista_pedidos"),
    path("mayorista/pedidos/<int:id>/<str:accion>/", views_mayorista.pedido_transicion, name="portal_mayorista_pedido_transicion"),
    path("mayorista/vendedores/", views_mayorista.vendedores_list, name="portal_mayorista_vendedores"),
    path("mayorista/vendedores/nuevo/", views_mayorista.vendedor_crear, name="portal_mayorista_vendedor_crear"),
    path("mayorista/vendedores/<int:id>/toggle/", views_mayorista.vendedor_toggle, name="portal_mayorista_vendedor_toggle"),
    path("mayorista/rendiciones/", views_mayorista.rendiciones_list, name="portal_mayorista_rendiciones"),
    path("mayorista/rendiciones/<int:id>/confirmar/", views_mayorista.rendicion_confirmar, name="portal_mayorista_rendicion_confirmar"),
    path("mayorista/reportes/", views_mayorista.reportes, name="portal_mayorista_reportes"),
    path("mayorista/mi-cuenta/", views_mayorista.mi_cuenta, name="portal_mayorista_mi_cuenta"),

    # Vendedor
    path("vendedor/dashboard/", views_vendedor.dashboard, name="portal_vendedor_dashboard"),
    path("vendedor/cambiar-password/", views_vendedor.cambiar_password, name="portal_vendedor_cambiar_password"),
    path("vendedor/pedido/nuevo/", views_vendedor.nuevo_pedido_paso1, name="portal_vendedor_pedido_paso1"),
    path("vendedor/pedido/nuevo/<int:tienda_id>/", views_vendedor.nuevo_pedido_paso2, name="portal_vendedor_pedido_paso2"),
    path("vendedor/pedido/nuevo/confirmar/", views_vendedor.nuevo_pedido_paso3, name="portal_vendedor_pedido_paso3"),
    path("vendedor/cobros/", views_vendedor.cobros_pendientes, name="portal_vendedor_cobros"),
    path("vendedor/cobros/<int:pago_id>/marcar/", views_vendedor.marcar_cobrado, name="portal_vendedor_marcar_cobrado"),
    path("vendedor/rendicion/", views_vendedor.rendicion_caja, name="portal_vendedor_rendicion"),

    # Tienda
    path("tienda/", views_tienda.marketplace, name="portal_tienda_marketplace"),
    path("tienda/mayorista/<int:mayorista_id>/", views_tienda.catalogo, name="portal_tienda_catalogo"),
    path("tienda/agregar/<int:producto_id>/", views_tienda.agregar_al_carrito, name="portal_tienda_agregar_carrito"),
    path("tienda/carrito/", views_tienda.carrito_ver, name="portal_tienda_carrito"),
    path("tienda/entrega/", views_tienda.entrega, name="portal_tienda_entrega"),
    path("tienda/confirmacion/<int:pedido_id>/", views_tienda.confirmacion, name="portal_tienda_confirmacion"),
    path("tienda/mis-pedidos/", views_tienda.mis_pedidos, name="portal_tienda_mis_pedidos"),

    # Administrador
    path("admin-panel/dashboard/", views_admin.dashboard, name="portal_admin_dashboard"),
    path("admin-panel/mayoristas/", views_admin.mayoristas_list, name="portal_admin_mayoristas"),
    path("admin-panel/mayoristas/<int:id>/toggle/", views_admin.mayorista_toggle, name="portal_admin_mayorista_toggle"),
    path("admin-panel/configuracion/", views_admin.configuracion, name="portal_admin_configuracion"),
    path("admin-panel/suscripciones/", views_admin.suscripciones, name="portal_admin_suscripciones"),
]
