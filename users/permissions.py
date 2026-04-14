from rest_framework import permissions

class IsSensorRole(permissions.BasePermission):
    """Acceso exclusivo para el Rol Sensor (POST de datos) [cite: 19]"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.rol == 'sensor'
        )

class IsAdminRole(permissions.BasePermission):
    """Acceso exclusivo para el Rol Admin (Lectura y Alertas) [cite: 20]"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.rol == 'admin'
        )