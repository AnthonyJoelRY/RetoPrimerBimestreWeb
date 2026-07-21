from django import forms

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


class MayoristaForm(forms.ModelForm):
    class Meta:
        model = Mayorista
        fields = "__all__"


class VendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = "__all__"


class TiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = "__all__"


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = "__all__"


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = "__all__"


class PedidoItemForm(forms.ModelForm):
    class Meta:
        model = PedidoItem
        fields = "__all__"


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = "__all__"


class RendicionForm(forms.ModelForm):
    class Meta:
        model = Rendicion
        fields = "__all__"
