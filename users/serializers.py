from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # Los campos definidos aquí son las "casillas" que verás en el navegador
        fields = ['username', 'password', 'rol']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            rol=validated_data.get('rol', 'admin')
        )
        return user