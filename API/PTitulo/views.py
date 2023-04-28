from django.http import Http404
from rest_framework import viewsets
from .models import Usuario
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import action
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.db.models import Q




class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            usuario.set_password(request.data.get('contrasena'))
            usuario.isActive = True
            usuario.isAdmin = False
            # generate a token for the new user and associate it with their account
            usuario.save()
            response_data = {'success': True, 'message': 'Usuario creado exitosamente.'}
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        # Handle validation errors
        error_data = serializer.errors
        for field, errors in error_data.items():
            error_data[field] = [str(e) for e in errors]
        error_details = {
            'code': status.HTTP_400_BAD_REQUEST,
            'message': 'Bad Request',
            'details': error_data
        }
        raise ValidationError(detail=error_details)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error_data = e.detail
            for field, errors in error_data.items():
                error_data[field] = [str(e) for e in errors]
            error_details = {
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Bad Request',
                'details': error_data
            }
            return Response({'success': False, 'error': error_details}, status=status.HTTP_400_BAD_REQUEST)

        fields_changed = False
        for field in serializer.fields:
            if field in request.data and getattr(instance, field) != request.data[field]:
                fields_changed = True
                break

        if not fields_changed:
            response_data = {'success': False, 'message': 'La información proporcionada es la misma.'}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # validar que la nueva contraseña no sea igual a la anterior
        new_password = request.data.get('contrasena')
        if new_password:
            current_password = instance.contrasena
            if check_password(new_password, current_password):
                response_data = {'success': False, 'message': 'La nueva contraseña no puede ser igual a la anterior.'}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save(force_update=True)

        if new_password:
            instance.set_password(new_password)
            instance.save()

        response_data = {'success': True, 'message': 'Usuario actualizado exitosamente.'}
        return Response(response_data)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            response_data = {'success': False, 'message': 'El usuario no existe.'}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        instance = self.get_object()
        instance.isActive = False
        instance.save()
        response_data = {'success': True, 'message': 'Usuario dado de baja correctamente.'}
        return Response(response_data, status=status.HTTP_200_OK)

class LoginViewSet(viewsets.ViewSet):
    queryset = Usuario.objects.none()
    serializer_class = LogInSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        data = request.data
        rut = data.get('rut')
        contrasena = data.get('contrasena')
        
        try:
            user = Usuario.objects.get(rut=rut)
        except Usuario.DoesNotExist:
            response_data = {'success': False, 'message': 'El usuario no existe.'}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        pass_valido = check_password(contrasena, user.contrasena)
        if not pass_valido:
            response_data = {'success': False, 'message': 'La contraseña no concuerda.'}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # crear o recuperar el token
        login_serializer = LogInSerializer(user)
        token_data = Token.objects.filter(user=user.user)
        token_serializer = TokenSerializer(token_data, many=True)
        login_data = {'usuario': login_serializer.data, 'tokens': token_serializer.data}
        response_data = {'success': True, 'message': 'Inicio de sesión exitoso', 'data': login_data}
        return Response(response_data, status=status.HTTP_200_OK)

class RecoverPasswordViewSet(viewsets.ViewSet):
    queryset = Usuario.objects.none()
    serializer_class = RecoverPasswordSerializer
    EMAIL_ERROR_MSG = "Error al enviar el correo electrónico"

    @action(detail=False, methods=['post'])
    def generar_password(self, request):
        # Obtener datos de la petición
        data = request.data
        rut = data.get('rut')

        # Buscar el usuario en la base de datos
        try:
            usuario = Usuario.objects.get(rut=rut)
        except Usuario.DoesNotExist:
            response_data = {'success': False, 'message': 'El usuario no existe.'}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Generar una nueva contraseña para el usuario
        nueva_contrasena = usuario.generate_password()

        # Enviar correo con la nueva contraseña al usuario
        email_sent = usuario.recover_email(nueva_contrasena)
        if not email_sent:
            response_data = {'success': False, 'message': 'Error al enviar el correo electrónico.'}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Actualizar la contraseña del usuario en la base de datos
        usuario.set_password(nueva_contrasena)
        usuario.save()

        # Devolver una respuesta satisfactoria
        response_data = {'success': True, 'message': 'Se ha generado una nueva contraseña y se ha enviado por correo electrónico.'}
        return Response(response_data, status=status.HTTP_200_OK)
    
class TipoMascotaViewSet(viewsets.ModelViewSet):
    queryset = TipoMascota.objects.all()
    serializer_class = TipoMascotaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({'success': False, 'message': 'Tipo de mascota no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nombre = serializer.validated_data.get('nombre')
        if TipoMascota.objects.filter(Q(nombre__iexact=nombre)).exists():
            return Response(
                {'success': False, 'message': 'Ya existe un tipo de mascota con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        response_data = {'success': True, 'message': 'Tipo de mascota creado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        nombre = serializer.validated_data.get('nombre')
        if nombre == instance.nombre:
            return Response(
                {'success': False, 'message': 'No se ha modificado el nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if TipoMascota.objects.filter(~Q(id=instance.id), Q(nombre__iexact=nombre)).exists():
            return Response(
                {'success': False, 'message': 'Ya existe un tipo de mascota con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_update(serializer)
        response_data = {'success': True, 'message': 'Tipo de mascota actualizado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response_data = {'success': True, 'message': 'Tipo de mascota eliminado exitosamente'}
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
    
class TipoAnuncioViewSet(viewsets.ModelViewSet):
    queryset = TipoAnuncio.objects.all()
    serializer_class = TipoAnuncioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({'success': False, 'message': 'Tipo de anuncio no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nombre = serializer.validated_data.get('nombre')
        if TipoAnuncio.objects.filter(Q(nombre__iexact=nombre)).exists():
            return Response(
                {'success': False, 'message': 'Ya existe un tipo de anuncio con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        response_data = {'success': True, 'message': 'Tipo de anuncio creado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        nombre = serializer.validated_data.get('nombre')
        if nombre == instance.nombre:
            return Response(
                {'success': False, 'message': 'No se ha modificado el nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if TipoAnuncio.objects.filter(~Q(id=instance.id), Q(nombre__iexact=nombre)).exists():
            return Response(
                {'success': False, 'message': 'Ya existe un tipo de anuncio con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_update(serializer)
        response_data = {'success': True, 'message': 'Tipo de anuncio actualizado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response_data = {'success': True, 'message': 'Tipo de anuncio eliminado exitosamente'}
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({'success': False, 'message': 'Estado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nombre = serializer.validated_data.get('nombre')
        if Estado.objects.filter(Q(nombre__iexact=nombre)).exists():
            return Response(
                {'success': False, 'message': 'Ya existe un estado con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        response_data = {'success': True, 'message': 'Estado creado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        nombre = serializer.validated_data.get('nombre')
        if nombre == instance.nombre:
            return Response(
                {'success': False, 'message': 'No se ha modificado el nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Estado.objects.filter(~Q(id=instance.id), Q(nombre__iexact=nombre)).exists():
            return Response(
                {'success': False, 'message': 'Ya existe un estado con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_update(serializer)
        response_data = {'success': True, 'message': 'Estado actualizado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response_data = {'success': True, 'message': 'Estado eliminado exitosamente'}
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


