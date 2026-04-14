from django.urls import path
from .views import IngestaDataView, EstadoActualView, ReporteHistoricoView

urlpatterns = [
    path('ingesta/', IngestaDataView.as_view(), name='ingesta-datos'),
    # Nuevas rutas analíticas
    path('estado-actual/', EstadoActualView.as_view(), name='estado-actual'),
    path('reporte/', ReporteHistoricoView.as_view(), name='reporte-historico'),
]