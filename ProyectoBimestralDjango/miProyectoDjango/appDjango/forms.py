import re
from django import forms
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from appDjango.models import Mayorista, Vendedor, Tienda, Producto, PlataformaConfig

TELEFONO_RE = re.compile(r"^[0-9]{7,15}$")
PIN_RE = re.compile(r"^[0-9]{4}$")


class MayoristaRegistroForm(forms.Form):
    nombre = forms.CharField(label="Nombre de la empresa", max_length=255)
    email = forms.EmailField(label="Correo electrónico")
    telefono = forms.CharField(
        label="Número de celular",
        max_length=15,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ej: 0991234567",
                "inputmode": "tel",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput, min_length=6
    )
    categoria = forms.ChoiceField(
        choices=Mayorista.CATEGORIA_CHOICES, label="Categoría"
    )

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()

        if not TELEFONO_RE.match(telefono):
            raise forms.ValidationError(
                "Ingresa un número válido utilizando únicamente números."
            )

        return telefono

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    def guardar(self):
        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )

        return Mayorista.objects.create(
            cuenta=user,
            nombre=self.cleaned_data["nombre"],
            telefono=self.cleaned_data["telefono"],
            categoria=self.cleaned_data["categoria"],
            plan="sin_asignar",
            tarifa_anual=0,
            porcentaje_comision=0,
            estado="pendiente_pago",
            fecha_vencimiento=None,
        )


class TiendaRegistroForm(forms.Form):
    nombre = forms.CharField(label="Nombre de la tienda", max_length=255)
    telefono = forms.CharField(label="Número de teléfono", max_length=20)
    pin = forms.CharField(
        label="PIN de seguridad (4 dígitos)", widget=forms.PasswordInput, max_length=4
    )
    pin_confirmacion = forms.CharField(
        label="Confirma el PIN", widget=forms.PasswordInput, max_length=4
    )
    direccion_texto = forms.CharField(
        label="Dirección referencial (opcional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if not TELEFONO_RE.match(telefono):
            raise forms.ValidationError("Ingresa un teléfono válido (solo números).")
        if (
            User.objects.filter(username=telefono).exists()
            or Tienda.objects.filter(telefono=telefono).exists()
        ):
            raise forms.ValidationError(
                "Ya existe una tienda registrada con ese teléfono."
            )
        return telefono

    def clean_pin(self):
        pin = self.cleaned_data["pin"]
        if not PIN_RE.match(pin):
            raise forms.ValidationError("El PIN debe tener exactamente 4 dígitos.")
        return pin

    def clean(self):
        cleaned = super().clean()
        if (
            cleaned.get("pin")
            and cleaned.get("pin_confirmacion")
            and cleaned["pin"] != cleaned["pin_confirmacion"]
        ):
            self.add_error("pin_confirmacion", "Los PIN no coinciden.")
        return cleaned

    def guardar(self):
        telefono = self.cleaned_data["telefono"]
        user = User.objects.create_user(
            username=telefono, password=self.cleaned_data["pin"]
        )

        return Tienda.objects.create(
            cuenta=user,
            nombre=self.cleaned_data["nombre"],
            telefono=telefono,
            direccion_texto=self.cleaned_data.get("direccion_texto") or "",
        )


class TiendaLoginForm(forms.Form):
    telefono = forms.CharField(
        label="Número de teléfono",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Número de teléfono",
                "inputmode": "tel",
                "autofocus": True,
            }
        ),
    )
    pin = forms.CharField(
        label="PIN de seguridad (4 dígitos)",
        max_length=4,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "PIN de 4 dígitos",
                "inputmode": "numeric",
                "maxlength": "4",
                "pattern": "[0-9]{4}",
            }
        ),
    )


class LoginEmailForm(forms.Form):

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={"placeholder": "Correo electrónico", "autofocus": True}
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Contraseña"}),
    )

    def clean_email(self):
        return self.cleaned_data["email"].lower()


class AdminLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Usuario administrador", "autofocus": True}
        )
        self.fields["password"].widget.attrs.update({"placeholder": "Contraseña"})


class VendedorCrearForm(forms.Form):
    nombre = forms.CharField(label="Nombre completo", max_length=255)
    email = forms.EmailField(label="Correo electrónico")
    tipo_perfil = forms.ChoiceField(
        choices=Vendedor.TIPO_PERFIL_CHOICES, label="Tipo de perfil"
    )
    producto_asignado = forms.ModelChoiceField(
        queryset=Producto.objects.none(),
        required=False,
        label="Producto asignado (solo perfil especializado)",
    )

    def __init__(self, *args, mayorista=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.mayorista = mayorista
        if mayorista is not None:
            self.fields["producto_asignado"].queryset = Producto.objects.filter(
                mayorista=mayorista
            )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    CONTRASENA_INICIAL = "cambiar123"

    def guardar(self):
        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=self.CONTRASENA_INICIAL,
        )

        return Vendedor.objects.create(
            cuenta=user,
            mayorista=self.mayorista,
            nombre=self.cleaned_data["nombre"],
            tipo_perfil=self.cleaned_data["tipo_perfil"],
            producto_asignado=self.cleaned_data.get("producto_asignado"),
            primer_login=True,
            activo=True,
        )


class ProductoMayoristaForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ["mayorista"]
        labels = {
            "nombre": "Nombre del producto",
            "foto_url": "URL de la fotografía",
            "precio": "Precio unitario ($)",
            "stock": "Stock disponible",
            "minimo_compra": "Mínimo por pedido",
            "unidad": "Unidad de medida",
            "activo": "Producto activo (visible en el catálogo de las tiendas)",
        }
        widgets = {
            "foto_url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }


class AjusteStockForm(forms.Form):
    stock = forms.IntegerField(min_value=0, label="Stock")


class MayoristaConfigComercialForm(forms.ModelForm):
    plan = forms.ChoiceField(
        label="Plan comercial",
        choices=[
            ("", "Selecciona un plan"),
            ("comision", "Solo comisión"),
            ("suscripcion", "Suscripción anual"),
            ("mixto", "Mixto"),
        ],
    )

    tarifa_anual = forms.DecimalField(
        label="Costo anual acordado ($)",
        required=False,
        min_value=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "step": "0.01",
                "min": "0",
                "placeholder": "Ej: 900.00",
            }
        ),
    )

    porcentaje_comision = forms.DecimalField(
        label="Porcentaje de comisión acordado (%)",
        required=False,
        min_value=Decimal("0.00"),
        max_value=Decimal("100.00"),
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "step": "0.01",
                "min": "0",
                "max": "100",
                "placeholder": "Ej: 3.50",
            }
        ),
    )

    fecha_vencimiento = forms.DateField(
        label="Fecha de vencimiento",
        required=False,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
            },
        ),
    )

    class Meta:
        model = Mayorista

        fields = [
            "plan",
            "tarifa_anual",
            "porcentaje_comision",
            "fecha_vencimiento",
        ]

    def clean(self):
        cleaned_data = super().clean()

        plan = cleaned_data.get("plan")
        tarifa_anual = cleaned_data.get("tarifa_anual")
        porcentaje_comision = cleaned_data.get("porcentaje_comision")
        fecha_vencimiento = cleaned_data.get("fecha_vencimiento")

        if plan == "comision":
            if porcentaje_comision is None or porcentaje_comision <= 0:
                self.add_error(
                    "porcentaje_comision",
                    "El plan por comisión necesita un porcentaje mayor que cero.",
                )

            cleaned_data["tarifa_anual"] = Decimal("0.00")
            cleaned_data["fecha_vencimiento"] = None

        elif plan == "suscripcion":
            if tarifa_anual is None or tarifa_anual <= 0:
                self.add_error(
                    "tarifa_anual",
                    "La suscripción necesita un costo anual mayor que cero.",
                )

            cleaned_data["porcentaje_comision"] = Decimal("0.00")

            if fecha_vencimiento is None:
                self.add_error(
                    "fecha_vencimiento",
                    "Debes indicar la fecha de vencimiento de la suscripción.",
                )

        elif plan == "mixto":
            if tarifa_anual is None or tarifa_anual <= 0:
                self.add_error(
                    "tarifa_anual",
                    "El plan mixto necesita un costo anual mayor que cero.",
                )

            if porcentaje_comision is None or porcentaje_comision <= 0:
                self.add_error(
                    "porcentaje_comision",
                    "El plan mixto necesita un porcentaje mayor que cero.",
                )

            if fecha_vencimiento is None:
                self.add_error(
                    "fecha_vencimiento",
                    "Debes indicar la fecha de vencimiento del plan mixto.",
                )

        else:
            raise forms.ValidationError("Selecciona un plan comercial válido.")

        if (
            fecha_vencimiento is not None
            and plan in ["suscripcion", "mixto"]
            and fecha_vencimiento < timezone.localdate()
        ):
            self.add_error(
                "fecha_vencimiento",
                "La fecha de vencimiento no puede estar en el pasado.",
            )

        return cleaned_data


class PlataformaConfigForm(forms.ModelForm):
    class Meta:
        model = PlataformaConfig
        fields = [
            "porcentaje_comision_default",
            "tarifa_suscripcion_anual",
            "tarifa_plan_mixto",
            "porcentaje_comision_mixto",
        ]
        labels = {
            "porcentaje_comision_default": "Porcentaje de comisión (%)",
            "tarifa_suscripcion_anual": "Costo anual ($)",
            "tarifa_plan_mixto": "Costo anual ($)",
            "porcentaje_comision_mixto": "Porcentaje de comisión (%)",
        }


class PedidoEntregaForm(forms.Form):
    nota_voz = forms.CharField(
        label="Nota para la entrega (opcional, puedes dictarla con el micrófono)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    lat = forms.FloatField(widget=forms.HiddenInput, required=True)
    lng = forms.FloatField(widget=forms.HiddenInput, required=True)
    telefono_contacto = forms.CharField(
        label="Teléfono de contacto",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Ej: 0991234567"}),
    )
    tipo_pago = forms.ChoiceField(
        label="Método de pago",
        choices=[
            ("efectivo", "Pagar en efectivo al recibir"),
            ("digital", "Pagar ahora (tarjeta / transferencia)"),
        ],
        widget=forms.RadioSelect,
        initial="efectivo",
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("lat") is None or cleaned.get("lng") is None:
            raise forms.ValidationError("Marca la ubicación de entrega en el mapa.")
        return cleaned


class AgregarCarritoForm(forms.Form):

    cantidad = forms.IntegerField(label="Cantidad", min_value=1)

    def __init__(self, *args, producto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.producto = producto

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if self.producto is not None:
            if not self.producto.verificar_minimo_compra(cantidad):
                raise forms.ValidationError(
                    "%s requiere un mínimo de %s unidades."
                    % (self.producto.nombre, self.producto.minimo_compra)
                )
            if not self.producto.verificar_stock(cantidad):
                raise forms.ValidationError(
                    "Solo hay %s unidades disponibles de %s."
                    % (self.producto.stock, self.producto.nombre)
                )
        return cantidad


class PedidoVendedorPagoForm(forms.Form):
    tipo_pago = forms.ChoiceField(
        label="Método de pago",
        choices=[
            ("efectivo", "Cobrar en efectivo"),
            ("digital", "La tienda paga por web (tarjeta / transferencia)"),
        ],
        widget=forms.RadioSelect,
        initial="efectivo",
    )
