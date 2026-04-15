from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoints de JWT (Login)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints de la App Users (Registro)
    path('api/users/', include('users.urls')),

    # Endpoints de Telemetría (Ingesta)
    path('api/telemetria/', include('telemetria.urls')),
]