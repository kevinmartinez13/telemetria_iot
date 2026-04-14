from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.settings import db_firestore
from users.permissions import IsSensorRole, IsAdminRole
import datetime

# Para la comunicación en tiempo real (WebSockets)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# --- 1. MÓDULO B: INGESTA DE TELEMETRÍA ---
class IngestaDataView(APIView):
    """
    Punto de entrada para los sensores.
    Recibe JSON, evalúa reglas de negocio, guarda en la nube (Firestore)
    y avisa en tiempo real si hay peligro.
    """
    # Solo usuarios con el rol 'sensor' pueden enviar datos aquí
    permission_classes = [IsSensorRole]

    def post(self, request):
        data = request.data # Recuperamos el JSON enviado por el sensor
        
        try:
            # --- EXTRACCIÓN Y LIMPIEZA ---
            # Extraemos valores, asignando 0 o 'Desconocido' si faltan datos
            id_servidor = data.get('id_servidor', 'Desconocido')
            cpu = float(data.get('cpu', 0))
            ram = float(data.get('ram', 0))
            temperatura = float(data.get('temperatura', 0))
            
            # --- MOTOR DE REGLAS ---
            # Lógica booleana: si la CPU supera 90% O la temperatura 75°C, es anomalía
            es_anomalia = cpu > 90.0 or temperatura > 75.0
            
            # --- PREPARACIÓN DEL PAQUETE (PAYLOAD) ---
            # Creamos el diccionario que se guardará en la base de datos
            payload = {
                "id_servidor": id_servidor,
                "cpu": cpu,
                "ram": ram,
                "temperatura": temperatura,
                "es_anomalia": es_anomalia,
                "fecha_registro": datetime.datetime.now() # Fecha y hora exacta del servidor
            }

            # --- A. PERSISTENCIA EN FIREBASE ---
            # .add() crea un nuevo documento con un ID aleatorio único (Histórico)
            db_firestore.collection('telemetria').add(payload)

            # --- B. NOTIFICACIÓN EN TIEMPO REAL (WEBSOCKETS) ---
            # Si el motor de reglas detectó un problema, notificamos a los Dashboards
            if es_anomalia:
                # Obtenemos la capa de canales de Django Channels
                channel_layer = get_channel_layer()
                # Enviamos el mensaje al grupo "alertas_criticas" de forma sincrónica
                async_to_sync(channel_layer.group_send)(
                    "alertas_criticas",
                    {
                        "type": "enviar_alerta", # Nombre de la función en el Consumer
                        "mensaje": f"⚠️ ALERTA CRÍTICA: {id_servidor}",
                        "datos": {
                            "servidor": id_servidor,
                            "cpu": f"{cpu}%",
                            "temp": f"{temperatura}°C"
                        }
                    }
                )

            # Respuesta exitosa al sensor
            return Response({
                "mensaje": "Datos procesados correctamente",
                "anomalia": es_anomalia
            }, status=status.HTTP_201_CREATED)

        except (ValueError, TypeError):
            # Error si mandaron texto donde debía ir un número (ej: cpu: "mucha")
            return Response({"error": "Formato de datos numéricos inválido"}, status=400)
        except Exception as e:
            # Error genérico (conexión a DB, error de lógica, etc.)
            return Response({"error": f"Error en el servidor: {str(e)}"}, status=500)


# --- 2. MÓDULO C.1: ESTADO ACTUAL (TIEMPO REAL) ---
class EstadoActualView(APIView):
    """
    Esta vista responde a peticiones GET.
    Su objetivo es consultar Firebase y armar un resumen de qué está pasando
    en cada servidor AHORA mismo.
    """
    # Solo los usuarios con rol de administrador pueden ver este monitoreo
    permission_classes = [IsAdminRole]

    def get(self, request):
        try:
            # --- PASO 1: CONSULTA A FIRESTORE ---
            # Accedemos a la colección 'telemetria'.
            # CRUCIAL: Usamos .order_by('fecha_registro', direction='DESCENDING')
            # Esto trae los documentos del más nuevo al más antiguo.
            # .stream() inicia la descarga de los datos.
            docs = db_firestore.collection('telemetria')\
                .order_by('fecha_registro', direction='DESCENDING').stream()

            # Diccionario vacío donde acumularemos los resultados únicos por servidor
            servidores = {}

            # --- PASO 2: PROCESAMIENTO DE LOS DOCUMENTOS ---
            for doc in docs:
                # Convertimos el documento de Firebase a un diccionario de Python
                item = doc.to_dict()
                
                # Obtenemos el ID del servidor (ej: "SRV-01", "SRV-02")
                srv_id = item.get('id_servidor')
                
                # --- PASO 3: LÓGICA DE FILTRADO (EL CORAZÓN DEL CÓDIGO) ---
                # Como los datos vienen ordenados del más reciente al más viejo:
                # La PRIMERA vez que aparece un ID de servidor, ese es su estado actual.
                if srv_id not in servidores:
                    # Si el servidor no está en nuestro diccionario, lo agregamos.
                    # Una vez agregado, la próxima vez que aparezca este srv_id 
                    # en el bucle, será ignorado (porque ya no entrará en este 'if').
                    servidores[srv_id] = {
                        "ultima_actualizacion": item.get('fecha_registro'),
                        "cpu": item.get('cpu'),
                        "temperatura": item.get('temperatura'),
                        # Traducimos el booleano 'es_anomalia' a un texto legible
                        "estado": "CRÍTICO" if item.get('es_anomalia') else "NORMAL"
                    }
            
            # --- PASO 4: RESPUESTA ---
            # Enviamos el diccionario 'servidores' que contiene solo un registro por servidor.
            return Response(servidores, status=status.HTTP_200_OK)
            
        except Exception as e:
            # En caso de fallo (ej. Firebase desconectado), enviamos el error.
            return Response({"error": str(e)}, status=500)


# --- 3. MÓDULO C.2: REPORTE HISTÓRICO (ANALÍTICA) ---
class ReporteHistoricoView(APIView):
    """
    Vista para generar estadísticas globales.
    Analiza todos los datos históricos para calcular promedios y picos.
    """
    # Seguridad: Solo usuarios Administradores pueden generar reportes
    permission_classes = [IsAdminRole]

    def get(self, request):
        try:
            # --- PASO 1: OBTENCIÓN DE DATOS ---
            # Traemos todos los documentos de la colección 'telemetria'
            # .stream() es más eficiente para leer grandes volúmenes de datos
            docs = db_firestore.collection('telemetria').stream()
            
            # --- PASO 2: INICIALIZACIÓN DE VARIABLES (ACUMULADORES) ---
            total_cpu = 0        # Sumará todos los porcentajes de CPU
            max_temp = 0         # Guardará la temperatura más alta encontrada
            conteo_anomalias = 0 # Contador de cuántas veces hubo alertas
            conteo_total = 0     # Contador de registros procesados

            # --- PASO 3: EL BUCLE DE PROCESAMIENTO (RECORRIDO) ---
            for doc in docs:
                # Extraemos el contenido del documento actual
                val = doc.to_dict()
                
                # Obtenemos valores numéricos (con 0 por defecto para evitar errores)
                cpu = val.get('cpu', 0)
                temp = val.get('temperatura', 0)
                
                # A. Acumulación para el promedio:
                total_cpu += cpu
                
                # B. Algoritmo de búsqueda de máximo:
                # Si la temperatura actual es mayor a la que teníamos guardada, la actualizamos
                if temp > max_temp:
                    max_temp = temp
                
                # C. Conteo de incidencias:
                # Si el registro fue marcado como anomalía en la ingesta, sumamos 1
                if val.get('es_anomalia'):
                    conteo_anomalias += 1
                
                # D. Contador general para saber cuántos datos existen
                conteo_total += 1

            # --- PASO 4: CÁLCULOS MATEMÁTICOS FINALES ---
            
            # Cálculo del Promedio de CPU:
            # Fórmula: Suma de valores / Cantidad de valores
            # Usamos un 'if' (operador ternario) para evitar el error de "división por cero"
            # si la base de datos está vacía.
            promedio_cpu = total_cpu / conteo_total if conteo_total > 0 else 0

            # --- PASO 5: RESPUESTA ESTRUCTURADA ---
            return Response({
                "analisis": {
                    "total_registros_procesados": conteo_total,
                    "promedio_carga_cpu": f"{round(promedio_cpu, 2)}%", # Redondeamos a 2 decimales
                    "pico_maximo_temperatura": f"{max_temp}°C",
                    "total_alertas_generadas": conteo_anomalias
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Si algo falla (ej. error de conexión), devolvemos el error 500
            return Response({"error": str(e)}, status=500)