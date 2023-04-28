from requests import Response
from rest_framework import serializers, status
from .models import *
from rest_framework.authtoken.models import Token


class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ['rut', 'nombre', 'apellido', 'contrasena', 'correo', 'foto', 'celular', 'isActive', 'isAdmin']
        ordering = ['rut', 'nombre', 'apellido', 'contrasena', 'correo', 'foto', 'celular', 'isActive', 'isAdmin']

    def update(self, instance, validated_data):
        # Verificar si el campo rut está cambiando
        if 'rut' in validated_data and instance.rut != validated_data['rut']:
            raise serializers.ValidationError("No se puede modificar el campo 'rut'")
        return super().update(instance, validated_data)

class LogInSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['rut', 'nombre', 'apellido', 'contrasena', 'correo', 'foto', 'celular', 'isActive', 'isAdmin']
        ordering = ['rut', 'nombre', 'apellido', 'contrasena', 'correo', 'foto', 'celular', 'isActive', 'isAdmin', 'token']

class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ('key', 'created')

class RecoverPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ['rut', 'contrasena']

class TipoMascotaSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoMascota
        fields = '__all__'

class TipoAnuncioSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoAnuncio
        fields = '__all__'       

class EstadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Estado
        fields = '__all__'

class MascotaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Mascota
        fields = '__all__'

class PosicionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Posicion
        fields = '__all__'

class AnuncioSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Anuncio
        fields = '__all__'