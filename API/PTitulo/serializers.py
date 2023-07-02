from requests import Response
from rest_framework import serializers, status
from .models import *
from rest_framework.authtoken.models import Token


class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ['rut', 'nombre', 'apellido', 'contrasena', 'correo', 'foto', 'celular', 'isActive', 'isAdmin', 'msgToken']
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
    isActive = serializers.ReadOnlyField()
    haveAnuncio = serializers.SerializerMethodField()

    class Meta:
        model = Mascota
        fields = ['id', 'nombre', 'foto_1', 'foto_2', 'tipo', 'dueno', 'isActive', 'haveAnuncio']

    def get_haveAnuncio(self, mascota):
        return Anuncio.objects.filter(mascota=mascota).exists()

class PosicionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Posicion
        fields = '__all__'

class AnuncioSerializer(serializers.ModelSerializer):
    mascota = serializers.PrimaryKeyRelatedField(queryset=Mascota.objects.all(), error_messages={
    'unique': 'Ya existe anuncio con esta mascota.',
    'required': 'Este campo es requerido.'
    })

    class Meta:
        model = Anuncio
        fields = '__all__'

class ReporteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reporte
        fields = ('id', 'nombre', 'descripcion', 'usuario', 'respuesta', 'admin', 'isClosed')

class RecompensaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Recompensa
        fields = '__all__'

class ReputacionSerializer(serializers.ModelSerializer):
    promedio = serializers.SerializerMethodField()


    class Meta:
        model = Reputacion
        fields = ['id', 'puntuacion', 'promedio', 'evaluador', 'usuario']

    def get_promedio(self, obj):
        # Calculate the average score for the reputation
        user_reputations = Reputacion.objects.filter(usuario=obj.usuario)
        total_score = sum(reputation.puntuacion for reputation in user_reputations)
        count = user_reputations.count()

        if count > 0:
            promedio = total_score / count
            return promedio

        return None