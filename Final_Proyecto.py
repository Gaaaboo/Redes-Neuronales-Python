# Importacion de librerias a utilizar
import cv2 #Open CV
import asyncio #Sincronizaciones
from telegram import Bot #Bot de telegram
from datetime import datetime #Para obtener hora y fecha del sistema
import subprocess
import time
import os

thres = 0.6  #Umbral aplicado para la deteccion de personas (Sensibilidad y confianza del modelo)

# Configuración de la cámara
cap = cv2.VideoCapture(0) # *Nota: Inidce 0 default de sistema e inidce 1 para externos
cap.set(3, 1280) # El ancho de fotogramas a 1280px
cap.set(4, 720) # El alto de fotogramas a 720px
cap.set(10, 70) # Ajustando el brillo inicial de la cámara *Editar si se toma el índice 1

# Configuración para la detección de personas
classNames = []
classFile = 'coco.names' # Nombre del modelo a tomar
with open(classFile, 'rt') as f: # Se ejecuta en modo de lectura *rt*
    classNames = f.read().rstrip('\n').split('\n') # Se realiza la lectura del archivo para ver las listas

configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt' # Ruta donde está la confg. del modelo entrenado
weightsPath = 'frozen_inference_graph.pb' # Ruta donde está el peso del modelo (weights)

# Configurando e inicializar la detección
# Creación de objeto net con los pesos para su uso
net = cv2.dnn_DetectionModel(weightsPath, configPath)
# Se establece el tamaño de entrada del modelo en px
net.setInputSize(320, 320)
# Se escalan valores de px con esa operación para facilitar la ejecución
net.setInputScale(1.0 / 127.5)
# Centrado de esos valores obtenidos para el procesamiento
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)  # Se juegan o intercalan los canales RB

# Configuración para la grabación de video
frame_width = int(cap.get(3)) # El ancho a tomar para la grabación del video (se toma de 3, 1280px)
frame_height = int(cap.get(4)) # El alto a tomar para la grabación del video (se toma de 4, 720px)
fourcc = cv2.VideoWriter_fourcc(*'XVID') # Codec para comprimir el video grabado
# Definiendo el nombre del video a guardar tomando identificadores como la fecha y hora (Evita duplicados)
video_name = f'Grabaciones_del_aula_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.avi'
# Ruta a almacenar el video
video_path = 'C:\\Users\\Gaaboo\\Documents\\Python\\Grabaciones_Auditorio\\' + video_name #(Ruta completa y única)
# Objeto de salida en OpenCv con FPS y dimensiones del frame
out = cv2.VideoWriter(video_path, fourcc, 20.0, (frame_width, frame_height))

# Configuración del bot de Telegram
bot_token = '6150390422:AAGZ5tz-AmI1Km_2_14fZ6Rtmreakb0QWyM' # Obtenido de la aplicación (Chat)
bot = Bot(token=bot_token) 
chat_id = '6438296642' # ID de la conversación donde se recibirán las alertas (Chat)

# Ruta para almacenar las grabaciones (Ubicacion principal)
ruta_grabaciones = 'C:\\Users\\Gaaboo\\Documents\\Python\\Grabaciones_Auditorio\\'
#Problemas de filtrado de personas
#Conteo de personas
# Variable para controlar el tiempo de la última notificación
last_notification_time = None

# Variable para controlar la grabación de video
is_recording = True # Confirma que la grabación está en activo y se utiliza en el ciclo

def capture_frame(image, box): # defino para capturar la imagen con el boxx
    x, y, w, h = box # Dimensionado de box
    persona_frame = image[y:y+h, x:x+w] # Definicion de frame de persona con box
    return persona_frame # Return a persona en frame

# Función para enviar la notificación por Telegram con el frame capturado
async def send_telegram_notification(image, box): # MAnda mensaje con el frame capturado 
    persona_frame = capture_frame(image, box)
    frame_name = 'Frame_Persona_Detectada.jpg'
    frame_path = ruta_grabaciones + frame_name
    cv2.imwrite(frame_path, persona_frame)
    
    current_time = datetime.now() # Toma el tiempo real
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S") # Formato a tomar
    message = f"Se ha detectado una persona en el siguiente horario: {formatted_time}."
    
    await bot.send_photo(chat_id, photo=open(frame_path, 'rb'), caption=message)
    os.remove(frame_path) 

while True:
    success, img = cap.read()
    if success:
        if is_recording:
            out.write(img)

        classIds, confs, bbox = net.detect(img, confThreshold=thres)
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

                    # Si el objeto detectado es una persona, enviar notificación
                    if classNames[classId - 1].lower() == 'person':
                        current_time = datetime.now()
                        if last_notification_time is None or (current_time - last_notification_time).total_seconds() > 90:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            # Utilizar run_until_complete para esperar la ejecución de la coroutine
                            loop.run_until_complete(send_telegram_notification(img, box))
                            last_notification_time = current_time

        # Redimensionar la imagen para visualización
        img = cv2.resize(img, (800, 600))
        # Muestra la ventana de la imagen
        cv2.imshow("Output", img)

        key = cv2.waitKey(1) & 0xFF # Espera la instrucción de presionar una tecla (q) y almacena en key
        if key == ord('e'):
            if is_recording: # Comprueba si se está grabando un video y, si es así, detiene la grabación
                is_recording = False
                out.release() # Se libera el objeto de grabación actual
                print(f'Video grabado en: {video_path}') # Imprime la ruta almacenada
                cap.release() # Procesos para cerrar ventanas
                cv2.destroyAllWindows()

                time.sleep(2) # Delay a 3 segundos
                # Pasados esos 3 segundos se ejecuta el programa con la siguiente ruta
                subprocess.run(['python', 'C:\\Users\\Gaaboo\\Documents\\Python\\UI.py'])
                break
            else: # Se repite el ciclo de la creación del objeto y etiquetado del video
                is_recording = True
                video_name = f'Grabaciones_del_aula_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.avi'
                video_path = 'C:\\Users\\Gaaboo\\Documents\\Python\\Grabaciones_Auditorio\\' + video_name
                out = cv2.VideoWriter(video_path, fourcc, 20.0, (frame_width, frame_height))
                print(f'Iniciando nueva grabación: {video_path}')

# Liberar la cámara y cerrar las ventanas de OpenCV
cap.release()
# cv2.destroyAllWindows()