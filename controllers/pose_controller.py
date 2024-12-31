import cv2
import numpy as np
import time
from models.pose_model import PoseModel  # Importar el modelo de poses

class PoseController:
    def __init__(self):
        self.pose_model = PoseModel()  # Instanciar el modelo de pose

    def draw_clothing(self, image, landmarks):
        """
        Dibuja un rectángulo simulando ropa en el cuerpo detectado.
        """
        if landmarks:
            # Acceder a los puntos clave desde landmarks.landmark
            left_shoulder = landmarks.landmark[self.pose_model.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks.landmark[self.pose_model.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks.landmark[self.pose_model.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks.landmark[self.pose_model.mp_pose.PoseLandmark.RIGHT_HIP]

            # Coordenadas de la "ropa"
            top_left = (int(left_shoulder.x * image.shape[1]), int(left_shoulder.y * image.shape[0]))
            bottom_right = (int(right_hip.x * image.shape[1]), int(right_hip.y * image.shape[0]))

            # Dibujar un rectángulo simulando la ropa
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), -1)

    def start_camera(self):
        """
        Inicia la cámara y muestra detecciones de pose con esqueleto y ropa simulada.
        """
        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Espejo Inteligente', cv2.WINDOW_NORMAL)

        # Mostrar el texto inicial "Espejo iniciando..."
        start_time = time.time()
        while time.time() - start_time < 2:  # Mostrar durante 2 segundos
            frame = np.zeros((600, 800, 3), dtype=np.uint8)  # Crear fondo negro
            cv2.putText(frame, "Espejo iniciando...", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Espejo Inteligente', frame)
            if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('Espejo Inteligente', cv2.WND_PROP_VISIBLE) < 1:
                cap.release()
                cv2.destroyAllWindows()
                return

        # Captura de video
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Error al acceder a la cámara.")
                    break

                # Convertir la imagen a RGB para Mediapipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                landmarks = self.pose_model.process_frame(rgb_frame)  # Usar el modelo para procesar el cuadro

                # Dibujar la pose detectada y la ropa
                if landmarks:
                    self.draw_clothing(frame, landmarks)

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
