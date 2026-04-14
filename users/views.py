from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User
from .serializers import RegisterSerializer
from core.settings import db_firestore  # Importamos la conexión a Firestore

class RegisterView(generics.CreateAPIView):
    """
    Esta clase maneja la creación de usuarios. 
    Hereda de CreateAPIView, que ya trae la lógica para recibir un POST,
    validar datos con un Serializer y guardar en la base de datos local.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # Permitimos que cualquier persona (sin estar logueada) acceda a esta vista
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Sobrescribimos el método 'create' para que, además de guardar en SQLite,
        haga una copia de los datos en Firebase.
        """

        # --- PASO 1: REGISTRO ESTÁNDAR EN DJANGO ---
        # super().create llama a la lógica original de DRF.
        # 1. Valida los datos recibidos contra el RegisterSerializer.
        # 2. Si son válidos, crea el registro en la tabla 'User' de SQLite/PostgreSQL.
        # 3. Retorna una instancia de 'Response' con los datos del usuario creado.
        response = super().create(request, *args, **kwargs)
        
        # Verificamos si Django logró crear el usuario correctamente (Status 201)
        if response.status_code == status.HTTP_201_CREATED:
            try:
                # --- PASO 2: OBTENCIÓN DE DATOS PARA SINCRONIZAR ---
                
                # Extraemos el username enviado en la petición original (JSON)
                username_reg = request.data.get('username')
                
                # Buscamos al usuario que acabamos de guardar en la DB local.
                # Lo hacemos para obtener el objeto completo de Django.
                user_instance = User.objects.get(username=username_reg)
                
                # --- PASO 3: SINCRONIZACIÓN CON FIREBASE ---
                
                # Definimos la ubicación en Firestore:
                # Entramos a la colección 'usuarios' y creamos (o seleccionamos) 
                # un documento cuyo ID único será el propio 'username'.
                user_ref = db_firestore.collection('usuarios').document(username_reg)
                
                # Guardamos los datos en la nube (Firestore).
                user_ref.set({
                    'username': user_instance.username,
                    # IMPORTANTE: user_instance.password NO es el texto plano.
                    # Es el hash (ej. pbkdf2_sha256$...). Esto protege la privacidad.
                    'contraseña': user_instance.password, 
                    'rol': user_instance.rol # Asumiendo que tu modelo User tiene un campo 'rol'
                })
                
                # --- PASO 4: FEEDBACK DE ÉXITO ---
                # Modificamos el cuerpo de la respuesta que se enviará al cliente (Frontend)
                # para confirmar que la sincronización con Firebase fue exitosa.
                response.data['firebase_sync'] = True
                
            except Exception as e:
                # --- PASO 5: MANEJO DE ERRORES EXTERNOS ---
                # Si algo falla con la conexión a Internet o Firebase (SDK):
                # No queremos romper toda la respuesta, porque el usuario YA se creó en Django.
                # Simplemente avisamos que la sincronización falló.
                response.data['firebase_error'] = f"Error al sincronizar: {str(e)}"
        
        # Retornamos la respuesta final al cliente (móvil, web, Postman, etc.)
        return response