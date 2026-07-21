from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required

# Django REST Framework
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions

# Serializers
from appDjango.serializers import (
    UserSerializer,
    GroupSerializer,
    MayoristaSerializer,
    VendedorSerializer,
    TiendaSerializer,
    ProductoSerializer,
    PedidoSerializer,
    PedidoItemSerializer,
    PagoSerializer,
    RendicionSerializer,
)

# Modelos
from appDjango.models import (
    Mayorista,
    Vendedor,
    Tienda,
    Producto,
    Pedido,
    PedidoItem,
    Pago,
    Rendicion,
)

# Formularios
from appDjango.forms import (
    MayoristaForm,
    VendedorForm,
    TiendaForm,
    ProductoForm,
    PedidoForm,
    PedidoItemForm,
    PagoForm,
    RendicionForm,
)


# Página principal
def index(request):
    """
    Presenta el menú principal del sistema.
    """
    mayoristas = Mayorista.objects.all()
    vendedores = Vendedor.objects.all()
    tiendas = Tienda.objects.all()
    productos = Producto.objects.all()
    pedidos = Pedido.objects.all()
    pagos = Pago.objects.all()
    rendiciones = Rendicion.objects.all()

    informacion_template = {
        "mayoristas": mayoristas,
        "vendedores": vendedores,
        "tiendas": tiendas,
        "productos": productos,
        "pedidos": pedidos,
        "pagos": pagos,
        "rendiciones": rendiciones,
        "numero_mayoristas": len(mayoristas),
        "numero_vendedores": len(vendedores),
        "numero_tiendas": len(tiendas),
        "numero_productos": len(productos),
        "numero_pedidos": len(pedidos),
        "numero_pagos": len(pagos),
        "numero_rendiciones": len(rendiciones),
    }

    return render(request, "index.html", informacion_template)


# Login
def ingreso(request):
    """
    Permite el ingreso de usuarios al sistema.
    """
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        print(form.errors)

        if form.is_valid():
            username = form.data.get("username")
            raw_password = form.data.get("password")

            user = authenticate(username=username, password=raw_password)

            if user is not None:
                login(request, user)
                return redirect(index)
    else:
        form = AuthenticationForm()

    informacion_template = {
        "form": form
    }

    return render(request, "registration/login.html", informacion_template)


# Logout
def logout_view(request):
    """
    Permite cerrar la sesión del usuario.
    """
    logout(request)
    messages.info(request, "Has salido del sistema")
    return redirect(index)


# ===================== Mayorista =====================

def listar_mayoristas(request):
    """
    Lista todos los mayoristas registrados en la base de datos.
    """
    mayoristas = Mayorista.objects.all()

    informacion_template = {
        "mayoristas": mayoristas,
        "numero_mayoristas": len(mayoristas),
    }

    return render(request, "listarMayoristas.html", informacion_template)


def obtener_mayorista(request, id):
    """
    Muestra la información de un mayorista específico.
    """
    mayorista = Mayorista.objects.get(pk=id)

    informacion_template = {
        "mayorista": mayorista
    }

    return render(request, "obtenerMayorista.html", informacion_template)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.add_mayorista", login_url="/entrando/login/")
def crear_mayorista(request):
    """
    Permite crear un mayorista desde Django.
    """
    if request.method == "POST":
        formulario = MayoristaForm(request.POST)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = MayoristaForm()

    diccionario = {
        "formulario": formulario
    }

    return render(request, "crearMayorista.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.change_mayorista", login_url="/entrando/login/")
def editar_mayorista(request, id):
    """
    Permite editar un mayorista.
    """
    mayorista = Mayorista.objects.get(pk=id)

    if request.method == "POST":
        formulario = MayoristaForm(request.POST, instance=mayorista)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = MayoristaForm(instance=mayorista)

    diccionario = {
        "formulario": formulario
    }

    return render(request, "editarMayorista.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.delete_mayorista", login_url="/entrando/login/")
def eliminar_mayorista(request, id):
    """
    Permite eliminar un mayorista.
    """
    mayorista = Mayorista.objects.get(pk=id)
    mayorista.delete()

    return redirect(index)


# ===================== Vendedor =====================

def listar_vendedores(request):
    """
    Lista todos los vendedores registrados en la base de datos.
    """
    vendedores = Vendedor.objects.all()

    informacion_template = {
        "vendedores": vendedores,
        "numero_vendedores": len(vendedores),
    }

    return render(request, "listarVendedores.html", informacion_template)


def obtener_vendedor(request, id):
    """
    Muestra la información de un vendedor específico.
    """
    vendedor = Vendedor.objects.get(pk=id)

    informacion_template = {
        "vendedor": vendedor
    }

    return render(request, "obtenerVendedor.html", informacion_template)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.add_vendedor", login_url="/entrando/login/")
def crear_vendedor(request):
    """
    Permite crear un vendedor desde Django.
    """
    if request.method == "POST":
        formulario = VendedorForm(request.POST)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = VendedorForm()

    diccionario = {
        "formulario": formulario
    }

    return render(request, "crearVendedor.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.change_vendedor", login_url="/entrando/login/")
def editar_vendedor(request, id):
    """
    Permite editar un vendedor.
    """
    vendedor = Vendedor.objects.get(pk=id)

    if request.method == "POST":
        formulario = VendedorForm(request.POST, instance=vendedor)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = VendedorForm(instance=vendedor)

    diccionario = {
        "formulario": formulario
    }

    return render(request, "editarVendedor.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.delete_vendedor", login_url="/entrando/login/")
def eliminar_vendedor(request, id):
    """
    Permite eliminar un vendedor.
    """
    vendedor = Vendedor.objects.get(pk=id)
    vendedor.delete()

    return redirect(index)


# ===================== Tienda =====================

def listar_tiendas(request):
    """
    Lista todas las tiendas registradas en la base de datos.
    """
    tiendas = Tienda.objects.all()

    informacion_template = {
        "tiendas": tiendas,
        "numero_tiendas": len(tiendas),
    }

    return render(request, "listarTiendas.html", informacion_template)


def obtener_tienda(request, id):
    """
    Muestra la información de una tienda específica.
    """
    tienda = Tienda.objects.get(pk=id)

    informacion_template = {
        "tienda": tienda
    }

    return render(request, "obtenerTienda.html", informacion_template)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.add_tienda", login_url="/entrando/login/")
def crear_tienda(request):
    """
    Permite crear una tienda desde Django.
    """
    if request.method == "POST":
        formulario = TiendaForm(request.POST)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = TiendaForm()

    diccionario = {
        "formulario": formulario
    }

    return render(request, "crearTienda.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.change_tienda", login_url="/entrando/login/")
def editar_tienda(request, id):
    """
    Permite editar una tienda.
    """
    tienda = Tienda.objects.get(pk=id)

    if request.method == "POST":
        formulario = TiendaForm(request.POST, instance=tienda)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = TiendaForm(instance=tienda)

    diccionario = {
        "formulario": formulario
    }

    return render(request, "editarTienda.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.delete_tienda", login_url="/entrando/login/")
def eliminar_tienda(request, id):
    """
    Permite eliminar una tienda.
    """
    tienda = Tienda.objects.get(pk=id)
    tienda.delete()

    return redirect(index)


# ===================== Producto =====================

def listar_productos(request):
    """
    Lista todos los productos registrados en la base de datos.
    """
    productos = Producto.objects.all()

    informacion_template = {
        "productos": productos,
        "numero_productos": len(productos),
    }

    return render(request, "listarProductos.html", informacion_template)


def obtener_producto(request, id):
    """
    Muestra la información de un producto específico.
    """
    producto = Producto.objects.get(pk=id)

    informacion_template = {
        "producto": producto
    }

    return render(request, "obtenerProducto.html", informacion_template)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.add_producto", login_url="/entrando/login/")
def crear_producto(request):
    """
    Permite crear un producto desde Django.
    """
    if request.method == "POST":
        formulario = ProductoForm(request.POST)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = ProductoForm()

    diccionario = {
        "formulario": formulario
    }

    return render(request, "crearProducto.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.change_producto", login_url="/entrando/login/")
def editar_producto(request, id):
    """
    Permite editar un producto.
    """
    producto = Producto.objects.get(pk=id)

    if request.method == "POST":
        formulario = ProductoForm(request.POST, instance=producto)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = ProductoForm(instance=producto)

    diccionario = {
        "formulario": formulario
    }

    return render(request, "editarProducto.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.delete_producto", login_url="/entrando/login/")
def eliminar_producto(request, id):
    """
    Permite eliminar un producto.
    """
    producto = Producto.objects.get(pk=id)
    producto.delete()

    return redirect(index)


# ===================== Pedido =====================

def listar_pedidos(request):
    """
    Lista todos los pedidos registrados en la base de datos.
    """
    pedidos = Pedido.objects.all()

    informacion_template = {
        "pedidos": pedidos,
        "numero_pedidos": len(pedidos),
    }

    return render(request, "listarPedidos.html", informacion_template)


def obtener_pedido(request, id):
    """
    Muestra la información de un pedido específico.
    """
    pedido = Pedido.objects.get(pk=id)

    informacion_template = {
        "pedido": pedido
    }

    return render(request, "obtenerPedido.html", informacion_template)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.add_pedido", login_url="/entrando/login/")
def crear_pedido(request):
    """
    Permite crear un pedido desde Django.
    """
    if request.method == "POST":
        formulario = PedidoForm(request.POST)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = PedidoForm()

    diccionario = {
        "formulario": formulario
    }

    return render(request, "crearPedido.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.change_pedido", login_url="/entrando/login/")
def editar_pedido(request, id):
    """
    Permite editar un pedido.
    """
    pedido = Pedido.objects.get(pk=id)

    if request.method == "POST":
        formulario = PedidoForm(request.POST, instance=pedido)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = PedidoForm(instance=pedido)

    diccionario = {
        "formulario": formulario
    }

    return render(request, "editarPedido.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.delete_pedido", login_url="/entrando/login/")
def eliminar_pedido(request, id):
    """
    Permite eliminar un pedido.
    """
    pedido = Pedido.objects.get(pk=id)
    pedido.delete()

    return redirect(index)


# ===================== PedidoItem =====================

def listar_items_pedido(request):
    """
    Lista todos los ítems de pedido registrados en la base de datos.
    """
    items_pedido = PedidoItem.objects.all()

    informacion_template = {
        "items_pedido": items_pedido,
        "numero_items_pedido": len(items_pedido),
    }

    return render(request, "listarItemsPedido.html", informacion_template)


def obtener_item_pedido(request, id):
    """
    Muestra la información de un ítem de pedido específico.
    """
    item_pedido = PedidoItem.objects.get(pk=id)

    informacion_template = {
        "item_pedido": item_pedido
    }

    return render(request, "obtenerItemPedido.html", informacion_template)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.add_pedidoitem", login_url="/entrando/login/")
def crear_item_pedido(request):
    """
    Permite crear un ítem de pedido desde Django.
    """
    if request.method == "POST":
        formulario = PedidoItemForm(request.POST)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = PedidoItemForm()

    diccionario = {
        "formulario": formulario
    }

    return render(request, "crearItemPedido.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.change_pedidoitem", login_url="/entrando/login/")
def editar_item_pedido(request, id):
    """
    Permite editar un ítem de pedido.
    """
    item_pedido = PedidoItem.objects.get(pk=id)

    if request.method == "POST":
        formulario = PedidoItemForm(request.POST, instance=item_pedido)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = PedidoItemForm(instance=item_pedido)

    diccionario = {
        "formulario": formulario
    }

    return render(request, "editarItemPedido.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.delete_pedidoitem", login_url="/entrando/login/")
def eliminar_item_pedido(request, id):
    """
    Permite eliminar un ítem de pedido.
    """
    item_pedido = PedidoItem.objects.get(pk=id)
    item_pedido.delete()

    return redirect(index)


# ===================== Pago =====================

def listar_pagos(request):
    """
    Lista todos los pagos registrados en la base de datos.
    """
    pagos = Pago.objects.all()

    informacion_template = {
        "pagos": pagos,
        "numero_pagos": len(pagos),
    }

    return render(request, "listarPagos.html", informacion_template)


def obtener_pago(request, id):
    """
    Muestra la información de un pago específico.
    """
    pago = Pago.objects.get(pk=id)

    informacion_template = {
        "pago": pago
    }

    return render(request, "obtenerPago.html", informacion_template)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.add_pago", login_url="/entrando/login/")
def crear_pago(request):
    """
    Permite crear un pago desde Django.
    """
    if request.method == "POST":
        formulario = PagoForm(request.POST)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = PagoForm()

    diccionario = {
        "formulario": formulario
    }

    return render(request, "crearPago.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.change_pago", login_url="/entrando/login/")
def editar_pago(request, id):
    """
    Permite editar un pago.
    """
    pago = Pago.objects.get(pk=id)

    if request.method == "POST":
        formulario = PagoForm(request.POST, instance=pago)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = PagoForm(instance=pago)

    diccionario = {
        "formulario": formulario
    }

    return render(request, "editarPago.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.delete_pago", login_url="/entrando/login/")
def eliminar_pago(request, id):
    """
    Permite eliminar un pago.
    """
    pago = Pago.objects.get(pk=id)
    pago.delete()

    return redirect(index)


# ===================== Rendicion =====================

def listar_rendiciones(request):
    """
    Lista todas las rendiciones registradas en la base de datos.
    """
    rendiciones = Rendicion.objects.all()

    informacion_template = {
        "rendiciones": rendiciones,
        "numero_rendiciones": len(rendiciones),
    }

    return render(request, "listarRendiciones.html", informacion_template)


def obtener_rendicion(request, id):
    """
    Muestra la información de una rendición específica.
    """
    rendicion = Rendicion.objects.get(pk=id)

    informacion_template = {
        "rendicion": rendicion
    }

    return render(request, "obtenerRendicion.html", informacion_template)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.add_rendicion", login_url="/entrando/login/")
def crear_rendicion(request):
    """
    Permite crear una rendición desde Django.
    """
    if request.method == "POST":
        formulario = RendicionForm(request.POST)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = RendicionForm()

    diccionario = {
        "formulario": formulario
    }

    return render(request, "crearRendicion.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.change_rendicion", login_url="/entrando/login/")
def editar_rendicion(request, id):
    """
    Permite editar una rendición.
    """
    rendicion = Rendicion.objects.get(pk=id)

    if request.method == "POST":
        formulario = RendicionForm(request.POST, instance=rendicion)
        print(formulario.errors)

        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = RendicionForm(instance=rendicion)

    diccionario = {
        "formulario": formulario
    }

    return render(request, "editarRendicion.html", diccionario)


@login_required(login_url="/entrando/login/")
@permission_required("appDjango.delete_rendicion", login_url="/entrando/login/")
def eliminar_rendicion(request, id):
    """
    Permite eliminar una rendición.
    """
    rendicion = Rendicion.objects.get(pk=id)
    rendicion.delete()

    return redirect(index)


# ViewSets para Django REST Framework

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver o editar usuarios.
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver o editar grupos.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class MayoristaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar mayoristas.
    """
    queryset = Mayorista.objects.all()
    serializer_class = MayoristaSerializer
    permission_classes = [permissions.IsAuthenticated]


class VendedorViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar vendedores.
    """
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = [permissions.IsAuthenticated]


class TiendaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar tiendas.
    """
    queryset = Tienda.objects.all()
    serializer_class = TiendaSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar productos.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PedidoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar pedidos.
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PedidoItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar ítems de pedido.
    """
    queryset = PedidoItem.objects.all()
    serializer_class = PedidoItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class PagoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar pagos.
    """
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAuthenticated]


class RendicionViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, editar y eliminar rendiciones.
    """
    queryset = Rendicion.objects.all()
    serializer_class = RendicionSerializer
    permission_classes = [permissions.IsAuthenticated]
