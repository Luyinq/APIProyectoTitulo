from django.urls import path, include
from .views import UsuarioViewSet, LoginViewSet, RecoverPasswordViewSet, TipoMascotaViewSet, TipoAnuncioViewSet, EstadoViewSet, MascotaViewSet, ReporteViewSet, PosicionViewSet, AnuncioViewSet, RecompensaViewSet, ReputacionViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('usuario', UsuarioViewSet)
router.register('tipo_mascota', TipoMascotaViewSet)
router.register('tipo_anuncio', TipoAnuncioViewSet)
router.register('estado', EstadoViewSet)
router.register('mascota', MascotaViewSet)
router.register('reporte', ReporteViewSet)
router.register('posicion', PosicionViewSet)
router.register('anuncio', AnuncioViewSet)
router.register('recompensa', RecompensaViewSet)
router.register('reputacion', ReputacionViewSet)
router.register('', LoginViewSet, basename='login')
router.register('', RecoverPasswordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('usuario/<int:pk>/', UsuarioViewSet.as_view({'put': 'update'}), name='usuario-update')
]