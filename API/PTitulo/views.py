from rest_framework import viewsets
from .models import Usuario
from .serializers import UsuarioSerializer, LogInSerializer, TokenSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import action
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if model_to_dict(serializer.instance) == request.data:
            # The data in the request did not change, so don't update the instance
            return Response("No se ha actualizado la información anterior.")

        instance = serializer.save(force_update=True)

        if request.data.get('contrasena'):
            instance.set_password(request.data.get('contrasena'))
            instance.save()

        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.isActive = False
        instance.save()
        return Response("Usuario dado de baja correctamente.")


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
            return Response("Usuario No Válido", status=status.HTTP_400_BAD_REQUEST)
        
        pass_valido = check_password(contrasena, user.contrasena)
        if not pass_valido:
            return Response("Password Incorrecta", status=status.HTTP_400_BAD_REQUEST)
        
        # crear o recuperar el token
        login_serializer = LogInSerializer(user)
        token_data = Token.objects.filter(user=user.user)
        token_serializer = TokenSerializer(token_data, many=True)
        serializer = {'usuario': login_serializer.data,
                    'token': token_serializer.data}
        return Response(serializer, status=status.HTTP_200_OK)