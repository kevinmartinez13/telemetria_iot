import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import telemetria.routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter({
    #maneja las peticiones HTTP normales de get post
    "http": get_asgi_application(),
    # Channels maneja las conexiones WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            # Aquí es donde se definen las rutas de WebSocket, que importamos desde telemetria.routing
            telemetria.routing.websocket_urlpatterns 
        )
    ),
})
