from django.http import Http404
from rest_framework import viewsets
from .models import Usuario
from .serializers import *
from rest_framework import status, permissions
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import action
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.db.models import Q



class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Permitir métodos GET, HEAD, OPTIONS
        return request.user.usuario.isAdmin  # Permitir solo si el usuario es un administrador

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({'success': False, 'message': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
            'success': False,
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
                'success': False,
                'details': error_data
            }
            return Response({'success': False, 'error': error_details}, status=status.HTTP_400_BAD_REQUEST)
        
         # check if the user is an admin and the request includes isAdmin
        if not request.user.usuario.isAdmin and 'isAdmin' in request.data:
            response_data = {'success': False, 'message': 'No tienes permisos para cambiar el atributo isAdmin.'}
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

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

        if request.user.usuario.isAdmin and instance != request.user.usuario:
            user = User.objects.get(username=instance.rut)
            user.delete()
            response_data = {'success': True, 'message': 'Usuario eliminado correctamente.'}
            return Response(response_data, status=status.HTTP_200_OK)
        
        elif instance == request.user.usuario:
            anuncios = Anuncio.objects.get(autor=instance.rut)
            anuncios.delete()
            instance.isActive = False
            instance.save()
            response_data = {'success': True, 'message': 'Usuario dado de baja correctamente.'}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'No tienes permiso para realizar esta acción'},
                            status=status.HTTP_403_FORBIDDEN)

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
        
        user.isActive = True
        user.save()
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
        email = usuario.correo
        cifrado = email[0:3] + '*'*(len(email)-7) + email[-4:]
        response_data = {'success': True, 'message': f'Se ha generado una nueva contraseña y se ha enviado por correo electrónico a {cifrado}'}
        return Response(response_data, status=status.HTTP_200_OK)
    
class TipoMascotaViewSet(viewsets.ModelViewSet):
    queryset = TipoMascota.objects.all()
    serializer_class = TipoMascotaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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

class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.all()
    serializer_class = MascotaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Obtener el usuario que realiza la solicitud
        user = request.user
        if user.usuario.isAdmin:
        # Obtener todos los reportes si el usuario es un administrador
            queryset = Mascota.objects.all()
        else:
        # Obtener los reportes del usuario
            queryset = Mascota.objects.filter(dueno=user.username)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({'success': False, 'message': 'Mascota no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = {'success': True, 'message': 'Mascota creada exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        #Check if any field has changed
        data_has_changed = False
        for field_name, value in serializer.validated_data.items():
            if getattr(instance, field_name) != value:
                data_has_changed = True
                break
        if not data_has_changed:
            return Response({'success': False, 'message': 'No se ha modificado ningún campo'}, status=status.HTTP_400_BAD_REQUEST)
         
        self.perform_update(serializer)
        response_data = {'success': True, 'message': 'Mascota actualizado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response_data = {'success': True, 'message': 'Mascota eliminada exitosamente'}
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Obtener el usuario que realiza la solicitud
        user = request.user
        if user.usuario.isAdmin:
        # Obtener todos los reportes si el usuario es un administrador
            queryset = Reporte.objects.all()
        else:
        # Obtener los reportes del usuario
            queryset = Reporte.objects.filter(usuario=user.username)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # Crear un nuevo diccionario con los valores predeterminados
        data = request.data.copy()
        data['admin'] = None
        data['isClosed'] = False
        data['respuesta'] = None
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response_data = {'success': True, 'message': 'Reporte creado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Obtener el usuario que realiza la solicitud
        user = request.user

        # Verificar si el usuario es un administrador
        if not user.usuario.isAdmin:
            return Response({'success': False, 'message': 'No eres administrador.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verificar si algún atributo ha cambiado
        admin_changed = 'admin' in serializer.validated_data and instance.admin != serializer.validated_data['admin']
        respuesta_changed = 'respuesta' in serializer.validated_data and instance.respuesta != serializer.validated_data['respuesta']

        if admin_changed or respuesta_changed:
            instance.admin = serializer.validated_data.get('admin', instance.admin)
            instance.respuesta = serializer.validated_data.get('respuesta', instance.respuesta)

            instance.save()

            response_data = {'success': True, 'message': 'Reporte cerrado exitosamente', 'data': serializer.data}
            return Response(response_data, status=status.HTTP_200_OK)

        # Si ningún atributo ha cambiado, retornar un mensaje de error
        return Response({'success': False, 'message': 'Debes generar una respuesta.'}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        # Obtener el usuario que realiza la solicitud
        user = request.user
        # Verificar si el usuario es un administrador
        if not user.usuario.isAdmin:
            return Response({'success': False, 'message': 'No eres administrador.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        instance = self.get_object()
        if instance.isClosed:
            response_data = {'success': False, 'message': 'El reporte ya está cerrado', 'data': {}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        instance.isClosed = True
        instance.save()

        response_data = {'success': True, 'message': 'Reporte cerrado exitosamente', 'data': {}}
        return Response(response_data, status=status.HTTP_200_OK)

class PosicionViewSet(viewsets.ModelViewSet):
    queryset = Posicion.objects.all()
    serializer_class = PosicionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Check if ad with the same position already exists
        latitude = serializer.validated_data['latitud']
        longitude = serializer.validated_data['longitud']
        anuncio = serializer.validated_data['anuncio']
        if self.queryset.filter(latitud=latitude, longitud=longitude, anuncio=anuncio).exists():
            return Response({'success': False, 'message': 'Anuncio con la misma posición ya existe'},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        response_data = {'success': True, 'message': 'Posición creada exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.anuncio.autor != request.user.usuario and not request.user.usuario.isAdmin:
            return Response({'success': False, 'message': 'No tienes permiso para realizar esta acción'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {'success': True, 'message': 'Posición actualizada exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.anuncio.autor != request.user.usuario and not request.user.usuario.isAdmin:
            return Response({'success': False, 'message': 'No tienes permiso para realizar esta acción'},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        response_data = {'success': True, 'message': 'Posición eliminada exitosamente'}
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class AnuncioViewSet(viewsets.ModelViewSet):
    queryset = Anuncio.objects.all()
    serializer_class = AnuncioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({'success': False, 'message': 'Anuncio no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['isDeleted'] = False
        serializer.validated_data['contacto'] = None
        mascota = serializer.validated_data['mascota']
        usuario = request.user
        if mascota.dueno.rut != usuario.usuario.rut:
            return Response({'success': False, 'message': 'La mascota seleccionada no concuerda con el usuario'}, status=status.HTTP_400_BAD_REQUEST)
        if Anuncio.objects.filter(Q(mascota=mascota)).exists():
            return Response(
                {'success': False, 'message': 'Ya existe un anuncio para esta mascota.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        response_data = {'success': True, 'message': 'Anuncio creado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if 'autor' in request.data:
            return Response({'success': False, 'message': 'No se puede actualizar el campo autor.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if 'contacto' in request.data and (instance.autor != request.user.usuario or request.user.usuario.isAdmin):
            # Allow modification of the 'contacto' field if the user is the author or an admin
            serializer = self.get_serializer(instance, data={'contacto': request.data['contacto']}, partial=True)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        mascota = serializer.validated_data.get('mascota')

        if mascota and mascota.dueno.rut != request.user.usuario.rut:
            return Response({'success': False, 'message': 'La mascota seleccionada no concuerda con el usuario'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if any field has changed
        data_has_changed = False
        for field_name, value in serializer.validated_data.items():
            if getattr(instance, field_name) != value:
                data_has_changed = True
                break

        if not data_has_changed:
            return Response({'success': False, 'message': 'No se ha modificado ningún campo'},
                            status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        response_data = {'success': True, 'message': 'Anuncio modificado exitosamente', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.autor != request.user.usuario and not request.user.usuario.isAdmin:
            return Response({'success': False, 'message': 'No tienes permiso para realizar esta acción'},
                            status=status.HTTP_403_FORBIDDEN)
        instance.isDeleted = True
        instance.save()
        response_data = {'success': True, 'message': 'Anuncio eliminado exitosamente'}
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class RecompensaViewSet(viewsets.ModelViewSet):
    queryset = Recompensa.objects.all()
    serializer_class = RecompensaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ReputacionViewSet(viewsets.ModelViewSet):
    queryset = Reputacion.objects.all()
    serializer_class = ReputacionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]