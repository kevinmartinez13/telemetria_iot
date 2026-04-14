INFORME TÉCNICO: SISTEMA DE TELEMETRÍA IoT CON DJANGO Y FIREBASE

Estudiante: Jonathan Aguilera
Proyecto: Telemetría de Servidores en Tiempo Real
Tecnologías: Django, Channels, Firebase Firestore, Postman

1. Introducción
El presente informe describe el desarrollo e implementación de un sistema de monitoreo de servidores en tiempo real. Este sistema permite capturar métricas clave como el uso de CPU y la temperatura, almacenarlas en la nube y generar alertas automáticas ante comportamientos anómalos. Para lograrlo, se emplea una arquitectura basada en Django con soporte ASGI, integrando Firebase Firestore como base de datos en la nube.

2. Configuración y Ejecución del Sistema

2.1 Preparación del Entorno
Para ejecutar correctamente el proyecto, se recomienda seguir los siguientes pasos en la terminal:

- Crear un entorno virtual:
  python -m venv venv

- Activar el entorno virtual (Windows):
  venv\Scripts\activate

- Instalar las dependencias necesarias:
  pip install django daphne channels djangorestframework djangorestframework-simplejwt firebase-admin

2.2 Ejecución del Sistema
El sistema utiliza Daphne como servidor ASGI para habilitar la comunicación en tiempo real mediante WebSockets:

- Ejecutar el servidor:
  python manage.py runserver

- Verificar que el sistema indique:
  "Starting ASGI/Daphne development server"

3. Arquitectura de la Solución

3.1 Gestión de Datos con Firebase
El almacenamiento de los datos de telemetría se realiza mediante Firebase Firestore. La conexión se establece utilizando un archivo de credenciales (firebase-sdk.json). El sistema implementa un mecanismo de streaming que permite leer y procesar los datos de manera eficiente y en tiempo real.

3.2 Módulo Analítico
El sistema incorpora un módulo analítico encargado de procesar los datos en memoria para optimizar el rendimiento. Este módulo realiza las siguientes funciones:

- Recupera todos los registros de la colección de telemetría.
- Calcula el promedio del uso de CPU.
- Identifica el valor máximo de temperatura registrado.

3.3 Comunicación en Tiempo Real
La comunicación en tiempo real se implementa mediante Django Channels. Cuando el sistema detecta valores críticos (temperatura superior a 75°C o uso de CPU mayor al 90%), se envía automáticamente una alerta a través de un Channel Layer hacia un grupo de clientes conectados, permitiendo notificar de forma inmediata a los administradores.

4. Guía de Pruebas con Postman

4.1 Ingesta de Datos
- Método: POST
- URL: http://127.0.0.1:8000/api/telemetria/ingesta/

- Cuerpo (JSON):
{
    "id_servidor": "SRV-PROD-01",
    "cpu": 95.0,
    "ram": 30.0,
    "temperatura": 85.0
}

4.2 Monitor de Alertas
- Protocolo: WebSocket
- URL: ws://127.0.0.1:8000/ws/alertas/

Resultado esperado:
Al enviar los datos anteriores, el sistema generará una alerta en tiempo real con el siguiente mensaje:
"⚠️ ALERTA CRÍTICA: SRV-PROD-01"

5. Conclusiones
El sistema desarrollado cumple con los principios de escalabilidad y eficiencia, al separar la gestión de usuarios (SQLite) del almacenamiento de datos de telemetría (Firebase). Esta arquitectura permite responder de manera inmediata ante eventos críticos, mejorando la supervisión y disponibilidad de los servidores monitoreados.

Se recomienda complementar este informe con capturas de pantalla del panel de Firebase y de las pruebas realizadas en Postman, con el fin de evidenciar el correcto funcionamiento del sistema.


6. Endpoints del Sistema
A continuación se listan los endpoints principales utilizados en el sistema de telemetría:

- WebSocket de alertas en tiempo real:
  ws://127.0.0.1:8000/ws/alertas/

- API de ingesta de datos:
  http://127.0.0.1:8000/api/telemetria/ingesta/

- API de estado actual:
  http://127.0.0.1:8000/api/telemetria/estado-actual/

- API de generación de reportes:
  http://127.0.0.1:8000/api/telemetria/reporte/
