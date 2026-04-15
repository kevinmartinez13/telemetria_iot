import json
from channels.generic.websocket import AsyncWebsocketConsumer


    # Este Consumer es el encargado de manejar las conexiones de todos los usuariosWebSocket para alertas en tiempo real a la vez.
class AlertaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # se conecta para recibir alertas"
        self.group_name = "alertas_criticas"
        # recive alertas del grupo "alertas_criticas"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        # Recibir mensajes
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def enviar_alerta(self, event):
       
        await self.send(text_data=json.dumps({
            "mensaje": event["mensaje"],
            #DATOS TEMPERATURA Y CPU
            "datos": event["datos"]
        }))