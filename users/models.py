from django.contrib.auth.models import AbstractUser
from django.db import models

# mondelo de como se guardan los usuarios, con su rol (sensor o admin)
class User(AbstractUser):
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