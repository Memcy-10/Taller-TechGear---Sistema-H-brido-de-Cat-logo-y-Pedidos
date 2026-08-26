from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(label="Correo")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=120)
    email = forms.EmailField(label="Correo")
    password = forms.CharField(label="Contraseña", min_length=6, widget=forms.PasswordInput)
    rol = forms.ChoiceField(
        label="Rol",
        choices=[
            ("usuario", "Usuario"),
            ("empleado", "Empleado"),
            ("administrador", "Administrador"),
        ],
    )


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
    productos = forms.CharField(
        widget=forms.Textarea,
        help_text='JSON de productos, por ejemplo: [{"nombre":"Laptop", "precio":100, "stock":1}]',
    )
    total = forms.DecimalField(min_value=0.01, decimal_places=2)
