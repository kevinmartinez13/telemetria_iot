from django.db import models

class Telemetria(models.Model):
    id_servidor = models.CharField(max_length=50)
    cpu = models.FloatField()
    ram = models.FloatField()
    temperatura = models.FloatField()
    es_anomalia = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id_servidor} - {self.fecha_registro}"