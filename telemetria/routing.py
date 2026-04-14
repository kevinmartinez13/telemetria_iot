from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Cambia .as_view() por .as_asgi()
    re_path(r'ws/alertas/$', consumers.AlertaConsumer.as_asgi()),
]