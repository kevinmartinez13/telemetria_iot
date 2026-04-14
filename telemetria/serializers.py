from rest_framework import serializers
from .models import Telemetria

class TelemetriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetria
        fields = ['id_servidor', 'cpu', 'ram', 'temperatura', 'es_anomalia', 'fecha_registro']
        read_only_fields = ['es_anomalia', 'fecha_registro']