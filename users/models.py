from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Definición de roles para cumplimiento de seguridad [cite: 16]
    ROLE_CHOICES = (
        ('sensor', 'Sensor (Máquina)'),
        ('admin', 'Administrador (Humano)'),
    )
    rol = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='admin'
    )

    def __str__(self):
        return f"{self.username} - {self.rol}"