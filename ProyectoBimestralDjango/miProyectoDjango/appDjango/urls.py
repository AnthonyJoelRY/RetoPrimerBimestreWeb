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
    # Página principal / menú
    path("", views.index, name="index"),

    # Mayoristas
    path("mayoristas/", views.listar_mayoristas, name="listar_mayoristas"),
    path("mayorista/<int:id>", views.obtener_mayorista, name="obtener_mayorista"),
    path("crear/mayorista", views.crear_mayorista, name="crear_mayorista"),
    path("editar/mayorista/<int:id>", views.editar_mayorista, name="editar_mayorista"),
    path(
        "eliminar/mayorista/<int:id>",
        views.eliminar_mayorista,
        name="eliminar_mayorista",
    ),

    # Vendedores
    path("vendedores/", views.listar_vendedores, name="listar_vendedores"),
    path("vendedor/<int:id>", views.obtener_vendedor, name="obtener_vendedor"),
    path("crear/vendedor", views.crear_vendedor, name="crear_vendedor"),
    path("editar/vendedor/<int:id>", views.editar_vendedor, name="editar_vendedor"),
    path(
        "eliminar/vendedor/<int:id>",
        views.eliminar_vendedor,
        name="eliminar_vendedor",
    ),

    # Tiendas
    path("tiendas/", views.listar_tiendas, name="listar_tiendas"),
    path("tienda/<int:id>", views.obtener_tienda, name="obtener_tienda"),
    path("crear/tienda", views.crear_tienda, name="crear_tienda"),
    path("editar/tienda/<int:id>", views.editar_tienda, name="editar_tienda"),
    path(
        "eliminar/tienda/<int:id>",
        views.eliminar_tienda,
        name="eliminar_tienda",
    ),

    # Productos
    path("productos/", views.listar_productos, name="listar_productos"),
    path("producto/<int:id>", views.obtener_producto, name="obtener_producto"),
    path("crear/producto", views.crear_producto, name="crear_producto"),
    path("editar/producto/<int:id>", views.editar_producto, name="editar_producto"),
    path(
        "eliminar/producto/<int:id>",
        views.eliminar_producto,
        name="eliminar_producto",
    ),

    # Pedidos
    path("pedidos/", views.listar_pedidos, name="listar_pedidos"),
    path("pedido/<int:id>", views.obtener_pedido, name="obtener_pedido"),
    path("crear/pedido", views.crear_pedido, name="crear_pedido"),
    path("editar/pedido/<int:id>", views.editar_pedido, name="editar_pedido"),
    path(
        "eliminar/pedido/<int:id>",
        views.eliminar_pedido,
        name="eliminar_pedido",
    ),

    # Ítems de pedido
    path("items-pedido/", views.listar_items_pedido, name="listar_items_pedido"),
    path(
        "item-pedido/<int:id>",
        views.obtener_item_pedido,
        name="obtener_item_pedido",
    ),
    path("crear/item-pedido", views.crear_item_pedido, name="crear_item_pedido"),
    path(
        "editar/item-pedido/<int:id>",
        views.editar_item_pedido,
        name="editar_item_pedido",
    ),
    path(
        "eliminar/item-pedido/<int:id>",
        views.eliminar_item_pedido,
        name="eliminar_item_pedido",
    ),

    # Pagos
    path("pagos/", views.listar_pagos, name="listar_pagos"),
    path("pago/<int:id>", views.obtener_pago, name="obtener_pago"),
    path("crear/pago", views.crear_pago, name="crear_pago"),
    path("editar/pago/<int:id>", views.editar_pago, name="editar_pago"),
    path(
        "eliminar/pago/<int:id>",
        views.eliminar_pago,
        name="eliminar_pago",
    ),

    # Rendiciones
    path("rendiciones/", views.listar_rendiciones, name="listar_rendiciones"),
    path("rendicion/<int:id>", views.obtener_rendicion, name="obtener_rendicion"),
    path("crear/rendicion", views.crear_rendicion, name="crear_rendicion"),
    path(
        "editar/rendicion/<int:id>",
        views.editar_rendicion,
        name="editar_rendicion",
    ),
    path(
        "eliminar/rendicion/<int:id>",
        views.eliminar_rendicion,
        name="eliminar_rendicion",
    ),

    # Login y logout
    path("saliendo/logout/", views.logout_view, name="logout_view"),
    path("entrando/login/", views.ingreso, name="login"),

    # API REST
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
