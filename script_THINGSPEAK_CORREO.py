import requests
import json
from datetime import datetime

# Configuración de ThingSpeak
THINGSPEAK_CHANNEL_ID = "123456"
THINGSPEAK_API_KEY = "TU_API_KEY"
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_API_KEY}&results=1"

# Configuración del Endpoint de la API de MOP
API_URL = "https://apimee.mop.gob.cl/api/v1/mediciones/superficiales/flujometro"

# Headers requeridos
headers = {
    "codigoObra": "123456",
    "timeStampOrigen": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "Content-Type": "application/json"
}

# Obtener el último dato desde ThingSpeak
response = requests.get(THINGSPEAK_URL)

log_message = ""

if response.status_code == 200:
    data = response.json()
    
    if "feeds" in data and len(data["feeds"]) > 0:
        feed = data["feeds"][0]
        caudal = feed.get("field1")
        fecha_hora_medicion = feed.get("created_at")

        if caudal is not None and fecha_hora_medicion is not None:
            caudal = "{:.2f}".format(float(caudal))
            fecha_dt = datetime.strptime(fecha_hora_medicion, "%Y-%m-%dT%H:%M:%SZ")
            fecha_medicion = fecha_dt.strftime("%Y-%m-%d")
            hora_medicion = fecha_dt.strftime("%H:%M:%S")

            payload = {
                "autenticacion": {
                    "password": "miPasswordSegura",
                    "rutEmpresa": "12345678-9",
                    "rutUsuario": "98765432-1"
                },
                "medicionSuperficialFlujometro": {
                    "caudal": caudal,
                    "fechaMedicion": fecha_medicion,
                    "horaMedicion": hora_medicion,
                    "totalizador": "1234567"
                }
            }

            # Enviar la medición a la API de MOP
            response_mop = requests.post(API_URL, headers=headers, data=json.dumps(payload))

            log_message = f"Código: {response_mop.status_code}, Respuesta: {response_mop.text}\n"

        else:
            log_message = f"Error: No se encontraron valores en ThingSpeak.\n"
    else:
        log_message = f"Error: No hay datos en ThingSpeak.\n"
else:
    log_message = f"Error al obtener datos de ThingSpeak: {response.status_code}\n  {log_message}"

# Guardar en un archivo log
# with open("/ruta/del/log.txt", "a") as log_file:
#     log_file.write(log_message)

# Enviar el log por correo
from smtplib import SMTP
from email.mime.text import MIMEText

def enviar_correo(log_message):
    remitente = "sal.de.epsom@gmail.com"
    destinatario = "sal.de.epsom@gmail.com"
    asunto = "Reporte Diario - Medición de Flujómetro"

    mensaje = MIMEText(log_message)
    mensaje["Subject"] = asunto
    mensaje["From"] = remitente
    mensaje["To"] = destinatario

    try:
        with SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(remitente, "uoun pxxp cpdz unlb")
            smtp.sendmail(remitente, destinatario, mensaje.as_string())
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

# Enviar correo con el resultado
enviar_correo(log_message)
