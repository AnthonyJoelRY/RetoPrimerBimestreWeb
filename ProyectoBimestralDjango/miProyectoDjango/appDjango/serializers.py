from django.contrib.auth.models import User, Group
from rest_framework import serializers

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


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class MayoristaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mayorista
        fields = "__all__"


class VendedorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vendedor
        fields = "__all__"


class TiendaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tienda
        fields = "__all__"


class ProductoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Producto
        fields = "__all__"


class PedidoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pedido
        fields = "__all__"


class PedidoItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PedidoItem
        fields = "__all__"


class PagoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pago
        fields = "__all__"


class RendicionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rendicion
        fields = "__all__"
