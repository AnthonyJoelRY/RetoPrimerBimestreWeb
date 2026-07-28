from django.urls import path, include

# Se importan las vistas de la aplicación
from appDjango import views

# Django REST Framework
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r"mayoristas", views.MayoristaViewSet)
router.register(r"vendedores", views.VendedorViewSet)
router.register(r"tiendas", views.TiendaViewSet)
router.register(r"productos", views.ProductoViewSet)
router.register(r"pedidos", views.PedidoViewSet)
router.register(r"items-pedido", views.PedidoItemViewSet)
router.register(r"pagos", views.PagoViewSet)
router.register(r"rendiciones", views.RendicionViewSet)


urlpatterns = [
    # Landing / autenticación
    path("", views.landing, name="portal_landing"),
    path(
        "registro/mayorista/",
        views.registro_mayorista,
        name="portal_registro_mayorista",
    ),
    path(
        "registro/mayorista/confirmacion/",
        views.registro_mayorista_confirmacion,
        name="portal_registro_mayorista_confirmacion",
    ),
    path("registro/tienda/", views.registro_tienda, name="portal_registro_tienda"),
    path("login/mayorista/", views.login_mayorista, name="portal_login_mayorista"),
    path("login/tienda/", views.login_tienda, name="portal_login_tienda"),
    path("login/vendedor/", views.login_vendedor, name="portal_login_vendedor"),
    path("login/admin/", views.login_admin, name="portal_login_admin"),
    path("salir/", views.logout_portal, name="portal_logout"),
    # Mayorista
    path(
        "mayorista/dashboard/",
        views.mayorista_dashboard,
        name="portal_mayorista_dashboard",
    ),
    path(
        "mayorista/productos/",
        views.mayorista_productos,
        name="portal_mayorista_productos",
    ),
    path(
        "mayorista/productos/nuevo/",
        views.mayorista_producto_crear,
        name="portal_mayorista_producto_crear",
    ),
    path(
        "mayorista/productos/<int:id>/editar/",
        views.mayorista_producto_editar,
        name="portal_mayorista_producto_editar",
    ),
    path(
        "mayorista/productos/<int:id>/eliminar/",
        views.mayorista_producto_eliminar,
        name="portal_mayorista_producto_eliminar",
    ),
    path(
        "mayorista/inventario/",
        views.mayorista_inventario,
        name="portal_mayorista_inventario",
    ),
    path(
        "mayorista/pedidos/", views.mayorista_pedidos, name="portal_mayorista_pedidos"
    ),
    path(
        "mayorista/pedidos/<int:id>/<str:accion>/",
        views.mayorista_pedido_transicion,
        name="portal_mayorista_pedido_transicion",
    ),
    path(
        "mayorista/vendedores/",
        views.mayorista_vendedores,
        name="portal_mayorista_vendedores",
    ),
    path(
        "mayorista/vendedores/nuevo/",
        views.mayorista_vendedor_crear,
        name="portal_mayorista_vendedor_crear",
    ),
    path(
        "mayorista/vendedores/<int:id>/toggle/",
        views.mayorista_vendedor_toggle,
        name="portal_mayorista_vendedor_toggle",
    ),
    path(
        "mayorista/rendiciones/",
        views.mayorista_rendiciones,
        name="portal_mayorista_rendiciones",
    ),
    path(
        "mayorista/rendiciones/<int:id>/confirmar/",
        views.mayorista_rendicion_confirmar,
        name="portal_mayorista_rendicion_confirmar",
    ),
    path(
        "mayorista/reportes/",
        views.mayorista_reportes,
        name="portal_mayorista_reportes",
    ),
    path(
        "mayorista/mi-cuenta/",
        views.mayorista_mi_cuenta,
        name="portal_mayorista_mi_cuenta",
    ),
    # Vendedor
    path(
        "vendedor/dashboard/",
        views.vendedor_dashboard,
        name="portal_vendedor_dashboard",
    ),
    path(
        "vendedor/cambiar-password/",
        views.vendedor_cambiar_password,
        name="portal_vendedor_cambiar_password",
    ),
    path(
        "vendedor/pedido/nuevo/",
        views.vendedor_pedido_paso1,
        name="portal_vendedor_pedido_paso1",
    ),
    path(
        "vendedor/pedido/nuevo/<int:tienda_id>/",
        views.vendedor_pedido_paso2,
        name="portal_vendedor_pedido_paso2",
    ),
    path(
        "vendedor/pedido/nuevo/confirmar/",
        views.vendedor_pedido_paso3,
        name="portal_vendedor_pedido_paso3",
    ),
    path("vendedor/cobros/", views.vendedor_cobros, name="portal_vendedor_cobros"),
    path(
        "vendedor/cobros/<int:pago_id>/marcar/",
        views.vendedor_marcar_cobrado,
        name="portal_vendedor_marcar_cobrado",
    ),
    path(
        "vendedor/rendicion/",
        views.vendedor_rendicion,
        name="portal_vendedor_rendicion",
    ),
    # Tienda
    path("tienda/", views.tienda_marketplace, name="portal_tienda_marketplace"),
    path(
        "tienda/mayorista/<int:mayorista_id>/",
        views.tienda_catalogo,
        name="portal_tienda_catalogo",
    ),
    path(
        "tienda/agregar/<int:producto_id>/",
        views.tienda_agregar_carrito,
        name="portal_tienda_agregar_carrito",
    ),
    path("tienda/carrito/", views.tienda_carrito, name="portal_tienda_carrito"),
    path("tienda/entrega/", views.tienda_entrega, name="portal_tienda_entrega"),
    path(
        "tienda/confirmacion/<int:pedido_id>/",
        views.tienda_confirmacion,
        name="portal_tienda_confirmacion",
    ),
    path(
        "tienda/mis-pedidos/",
        views.tienda_mis_pedidos,
        name="portal_tienda_mis_pedidos",
    ),
    # Administrador
    path(
        "admin-panel/dashboard/", views.admin_dashboard, name="portal_admin_dashboard"
    ),
    path(
        "admin-panel/mayoristas/",
        views.admin_mayoristas,
        name="portal_admin_mayoristas",
    ),
    path(
        "admin-panel/mayoristas/<int:id>/toggle/",
        views.admin_mayorista_toggle,
        name="portal_admin_mayorista_toggle",
    ),
    path(
        "admin-panel/mayoristas/<int:id>/configuracion/",
        views.admin_mayorista_configuracion,
        name="portal_admin_mayorista_configuracion",
    ),
    path(
        "admin-panel/configuracion/",
        views.admin_configuracion,
        name="portal_admin_configuracion",
    ),
    path(
        "admin-panel/suscripciones/",
        views.admin_suscripciones,
        name="portal_admin_suscripciones",
    ),
    # API REST
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
