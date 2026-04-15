from django.urls import re_path
from . import consumers

# rutas de WebSocket para alertas en tiempo real
websocket_urlpatterns = [
    # R = Raw ws alertas
    re_path(r'ws/alertas/$', consumers.AlertaConsumer.as_asgi()),
]