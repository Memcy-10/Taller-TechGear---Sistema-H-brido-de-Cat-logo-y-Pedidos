from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(label="Correo")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class UserForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=120)
    email = forms.EmailField(label="Correo")
    password = forms.CharField(label="Contraseña", min_length=6, widget=forms.PasswordInput)
    rol = forms.ChoiceField(choices=[
        ("usuario", "Usuario"),
        ("empleado", "Empleado"),
        ("administrador", "Administrador"),
    ])


class ProductForm(forms.Form):
    nombre = forms.CharField(max_length=120)
    descripcion = forms.CharField(widget=forms.Textarea, required=False)
    precio = forms.DecimalField(min_value=0.01, decimal_places=2)
    stock = forms.IntegerField(min_value=0)
    categoria = forms.CharField(max_length=80, required=False)
    imagen = forms.ImageField(label="Imagen del producto", required=False)


class OrderForm(forms.Form):
    nombre_usuario = forms.CharField(
        label="Nombre de usuario",
        max_length=120,
        help_text="El nombre que quedará registrado en la orden.",
    )
    id_usuario = forms.CharField(
        label="ID de usuario (opcional)",
        max_length=120,
        required=False,
        help_text="Si lo dejas vacío, se generará un ID de prueba automáticamente.",
    )


class OrderManagementForm(forms.Form):
    nombre_usuario = forms.CharField(
        label="Nombre del cliente",
        max_length=120,
    )
    id_usuario = forms.CharField(
        label="ID del cliente",
        max_length=120,
        required=False,
    )
    estado = forms.ChoiceField(
        label="Estado",
        choices=[
            ("pendiente", "Pendiente"),
            ("en_proceso", "En proceso"),
            ("completada", "Completada"),
            ("cancelada", "Cancelada"),
        ],
    )
