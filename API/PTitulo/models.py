from itertools import cycle
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re, random, string, requests

#Validar Rut
def is_valid_rut(rut):
    rut = rut.upper()
    rut = rut.replace("-", "")
    rut = rut.replace(".", "")
    aux = rut[:-1]
    dv = rut[-1:]

    if dv == 'K':
        dv = 10
    elif not dv.isdigit():
        return False

    if not aux.isdigit():
        return False

    revertido = map(int, reversed(str(aux)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(revertido, factors))
    res = (-s) % 11

    if str(res) == str(dv):
        return True
    else:
        return False

def validate_chilean_rut(value):
    if not is_valid_rut(value):
        raise ValidationError("El RUT ingresado no es válido.")

def validate_alphanumeric(value):
    if not value.isalnum():
        raise ValidationError('El campo debe contener solo letras o números')

def validate_min(value):
    if len(value) < 2:
        raise ValidationError('El campo debe tener al menos 2 caracteres')

def validate_only_letters(value):
    if not value.isalpha():
        raise ValidationError('El campo debe contener solo letras')

def validate_password_complexity(value):
    if len(value) < 6:
        raise ValidationError('La contraseña debe tener al menos 6 carácteres')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
    if not re.search(r'[a-z]', value):
        raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
    if not re.search(r'[0-9]', value):
        raise ValidationError('La contraseña debe contener al menos un número.')

#Modelo Usuario
class Usuario(models.Model):
    rut = models.CharField(primary_key=True, max_length=9, validators=[validate_chilean_rut, validate_alphanumeric,], verbose_name="Rut", help_text="Ingrese rut sin puntos ni guiones")
    nombre = models.CharField(max_length=20, validators=[validate_min, validate_only_letters], verbose_name="Nombre")
    apellido = models.CharField(max_length=20, validators=[validate_min, validate_only_letters], verbose_name="Apellido")
    contrasena = models.CharField(max_length=20, validators=[validate_password_complexity], verbose_name="Contraseña")
    correo = models.EmailField(max_length=50, verbose_name="Correo", unique=True)
    foto = models.CharField(max_length=256, null=True, default=None, blank=True, verbose_name="Foto")
    celular = models.IntegerField(verbose_name="Celular", validators=[MaxValueValidator(999999999), MinValueValidator(900000000)], unique=True)
    isActive = models.BooleanField(default=True, verbose_name="Activo")
    isAdmin = models.BooleanField(default=False, verbose_name="Admin")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="User")


    @classmethod
    def set_password(cls, raw_password):
        return make_password(raw_password)

    def set_password(self, raw_password):
        self.contrasena = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)

    def __str__(self):
        return self.rut

    def save(self, *args, **kwargs):
        if not self.user:
            self.user = User.objects.create_user(username=self.rut)
        super().save(*args, **kwargs)
        Token.objects.get_or_create(user=self.user)
    
    def generate_password(self):
        while True:
            # Generar contraseña aleatoria de 8 caracteres
            contrasena = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            # Verificar si cumple con los criterios
            if (len(contrasena) >= 6 and
                any(char.isupper() for char in contrasena) and
                any(char.islower() for char in contrasena) and
                any(char.isdigit() for char in contrasena)):
                return contrasena
    
    def recover_email(self, password):
        url = 'https://api.emailjs.com/api/v1.0/email/send'
        data = {
            'service_id': 'service_7nzmn9h',
            'template_id': 'template_bl5i8ce',
            'user_id': 'WQrwC2ydtySqBDjoN',
            'template_params': {
                'from_name': "PetCuy",
                'username': self.nombre + " " + self.apellido,
                'password': password,
                'email': self.correo,
            },
            'accessToken': 'GvevPGf_fCXSL9kEBvfLS'
        }
        response = requests.post(url, json=data)
        if response.ok:
            return True
        else:
            return False