import cv2
import mediapipe as mp
import numpy as np
import time
from models.pose_model import PoseModel  # Importar el modelo de poses


class PoseController:
    def __init__(self, polera_path):
        self.pose_model = PoseModel()  # Instanciar el modelo de pose
        self.polera = cv2.imread(polera_path, cv2.IMREAD_UNCHANGED)  # Cargar la imagen de la polera

    def overlay_clothing(self, frame, landmarks):
        """
        Superpone la polera sobre el torso de la persona.
        """
        if landmarks:
            # Coordenadas de los puntos clave
            h, w, _ = frame.shape
            left_shoulder = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP]
            nose = landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE]  # Referencia para el cuello

            # Convertir coordenadas normalizadas a píxeles
            left_shoulder_px = (int(left_shoulder.x * w), int(left_shoulder.y * h))
            right_shoulder_px = (int(right_shoulder.x * w), int(right_shoulder.y * h))
            left_hip_px = (int(left_hip.x * w), int(left_hip.y * h))
            nose_px = (int(nose.x * w), int(nose.y * h))

            # Calcular el ancho de la polera basado en los hombros y un margen
            width = int(np.linalg.norm(np.array(right_shoulder_px) - np.array(left_shoulder_px))) + 100  # Margen extra

            # Calcular el alto de la polera desde la nariz hasta la cadera
            height = int(np.linalg.norm(np.array(left_hip_px) - np.array(nose_px))) + 20  # Margen extra

            # Redimensionar la polera
            resized_polera = cv2.resize(self.polera, (width, height))

            # Superponer la polera en el torso
            x_min = min(left_shoulder_px[0], right_shoulder_px[0]) - 50  # Ajustar horizontalmente para centrar
            y_min = nose_px[1] + 20  # Comenzar desde el cuello
            self.overlay_image(frame, resized_polera, x_min, y_min)


    def overlay_image(self, frame, overlay, x, y):
        """
        Superpone una imagen (overlay) con transparencia sobre el frame principal.
        """
        overlay_h, overlay_w, _ = overlay.shape
        for i in range(overlay_h):
            for j in range(overlay_w):
                if y + i >= frame.shape[0] or x + j >= frame.shape[1]:
                    continue
                alpha = overlay[i, j, 3] / 255.0  # Canal alfa
                frame[y + i, x + j] = alpha * overlay[i, j, :3] + (1 - alpha) * frame[y + i, x + j]

    def draw_landmarks_with_labels(self, frame, landmarks):
        """
        Dibuja los puntos clave en el frame junto con sus etiquetas.
        """
        h, w, _ = frame.shape
        for idx, landmark in enumerate(landmarks.landmark):
            # Convertir las coordenadas normalizadas a píxeles
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # Dibujar un punto
            cv2.putText(frame, str(idx), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)  # Etiqueta

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

                # Dibujar los puntos clave y la ropa
                if landmarks:
                    self.draw_landmarks_with_labels(frame, landmarks)
                    self.overlay_clothing(frame, landmarks)

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
