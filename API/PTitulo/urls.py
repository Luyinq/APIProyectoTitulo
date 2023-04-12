from django.urls import path, include
from .views import UsuarioViewSet, LoginViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('usuario', UsuarioViewSet)
router.register('login', LoginViewSet, basename='login')

urlpatterns = [
    path('', include(router.urls)),
    path('usuario/<int:pk>/', UsuarioViewSet.as_view({'put': 'update'}), name='usuario-update')

]