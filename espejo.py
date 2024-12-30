import cv2
import mediapipe as mp
import numpy as np
import time

# Inicializar Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Función para superponer un modelo de ropa (simple rectángulo)
def draw_clothing(image, landmarks):
    if landmarks:
        # Obtener puntos clave de los hombros y la cintura
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        # Coordenadas de la "ropa"
        top_left = (int(left_shoulder.x * image.shape[1]), int(left_shoulder.y * image.shape[0]))
        bottom_right = (int(right_hip.x * image.shape[1]), int(right_hip.y * image.shape[0]))

        # Dibujar un rectángulo simulando la ropa
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), -1)

# Configuración de la ventana
cap = cv2.VideoCapture(0)
cv2.namedWindow('Espejo Inteligente', cv2.WINDOW_NORMAL)

# Maximizar la ventana
#cv2.setWindowProperty('Espejo Inteligente', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Mostrar el texto inicial "Espejo iniciando..."
start_time = time.time()
while time.time() - start_time < 2:  # Mostrar durante 2 segundos
    frame = np.zeros((600, 800, 3), dtype=np.uint8)  # Crear fondo negro
    cv2.putText(frame, "Espejo iniciando...", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Espejo Inteligente', frame)
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('Espejo Inteligente', cv2.WND_PROP_VISIBLE) < 1:
        cap.release()
        cv2.destroyAllWindows()
        exit()

# Captura de video
try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error al acceder a la cámara.")
            break

        # Convertir la imagen a RGB para Mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        # Dibujar pose detectada
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            draw_clothing(frame, results.pose_landmarks.landmark)

        # Mostrar el resultado
        cv2.imshow('Espejo Inteligente', frame)

        # Salir con la tecla 'q' o cerrar la ventana
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('Espejo Inteligente', cv2.WND_PROP_VISIBLE) < 1:
            break
except Exception as e:
    print(f"Error inesperado: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()

