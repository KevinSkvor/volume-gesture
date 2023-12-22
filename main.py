import cv2
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Función para calcular la distancia euclidiana entre dos puntos
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# Función para ajustar el volumen
def set_volume(volume_controller, hand_distance, max_distance):
    normalized_distance = min(hand_distance / max_distance, 1.0)
    volume = int(normalized_distance * 100)
    volume_controller.SetMasterVolumeLevelScalar(volume / 100, None)

# Inicializar la cámara
cap = cv2.VideoCapture(0)

# Inicializar el controlador de volumen
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_controller = cast(interface, POINTER(IAudioEndpointVolume))

# Variables para el seguimiento de la mano
hand_start = (0, 0)
max_hand_distance = 300

while True:
    # Capturar el fotograma de la cámara
    ret, frame = cap.read()

    # Voltear el fotograma horizontalmente para obtener una vista del espejo
    frame = cv2.flip(frame, 1)

    # Convertir el fotograma a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detección de bordes
    edges = cv2.Canny(gray, 50, 150)

    # Encontrar contornos
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Filtrar contornos pequeños
        if cv2.contourArea(contour) > 1000:
            # Obtener el centro del contorno
            M = cv2.moments(contour)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            # Dibujar un círculo en el centro del contorno
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

            # Calcular la distancia entre el centro y la posición inicial de la mano
            hand_distance = calculate_distance((cx, cy), hand_start)

            # Ajustar el volumen según la distancia
            set_volume(volume_controller, hand_distance, max_hand_distance)

    # Mostrar la imagen
    cv2.imshow('Volume Control', frame)

    # Romper el bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
