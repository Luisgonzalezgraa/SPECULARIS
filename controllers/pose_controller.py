import cv2
import mediapipe as mp
import numpy as np
import time
from models.pose_model import PoseModel  # Importar el modelo de poses


class PoseController:
    def __init__(self, asset_paths):
            """
            Inicializa el controlador con las imágenes para cada categoría.
            """
            self.pose_model = PoseModel()  # Instanciar el modelo de pose
            self.assets = {
                "cabeza": [cv2.imread(path, cv2.IMREAD_UNCHANGED) for path in asset_paths.get("cabeza", [])],
                "cuello": [cv2.imread(path, cv2.IMREAD_UNCHANGED) for path in asset_paths.get("cuello", [])],
                "torso": [cv2.imread(path, cv2.IMREAD_UNCHANGED) for path in asset_paths.get("torso", [])],
            }
            self.current_indices = {"cabeza": 0, "cuello": 0, "torso": 0}  # Índices actuales de cada categoría

    def overlay_clothing(self, frame, landmarks, category):
        """
        Superpone la ropa correspondiente a una categoría específica sobre la persona.
        """
        if landmarks and category in self.assets and self.assets[category]:
            # Seleccionar el ítem actual de la categoría
            current_item = self.assets[category][self.current_indices[category]]

            # Coordenadas de los puntos clave
            h, w, _ = frame.shape
            left_shoulder = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP]
            
            nose = landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE]  # Referencia para el cuello
            
            ear_left = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_EAR] # Referencia para la cabeza
            ear_right = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_EAR]
            
            mouth_right = landmarks.landmark[mp.solutions.pose.PoseLandmark.MOUTH_RIGHT]  # Referencia a la boca
            mouth_left = landmarks.landmark[mp.solutions.pose.PoseLandmark.MOUTH_LEFT]  

            # Convertir coordenadas normalizadas a píxeles
            left_shoulder_px = (int(left_shoulder.x * w), int(left_shoulder.y * h))
            right_shoulder_px = (int(right_shoulder.x * w), int(right_shoulder.y * h))
            left_hip_px = (int(left_hip.x * w), int(left_hip.y * h))
            nose_px = (int(nose.x * w), int(nose.y * h))
            ear_left_px = (int(ear_left.x * w), int(ear_left.y * h))
            ear_right_px = (int(ear_right.x * w), int(ear_right.y * h))
            mouth_right_px = (int(mouth_right.x * w), int(mouth_right.y * h))
            mouth_left_px = (int(mouth_left.x * w), int(mouth_left.y * h))

            # Ajustar las posiciones y dimensiones según la categoría
            if category == "torso":
                # Calcular el ancho de la prenda basado en los hombros y un margen
                width = int(np.linalg.norm(np.array(right_shoulder_px) - np.array(left_shoulder_px))) + 120

                # Calcular la altura de la prenda desde el hombro izquierdo hasta la cadera izquierda
                height = int(np.linalg.norm(np.array(left_hip_px) - np.array(left_shoulder_px))) + 85  # Margen extra

                x_min = min(left_shoulder_px[0], right_shoulder_px[0]) - 60  # Ajustar horizontalmente para centrar

                # La posición inicial vertical basada en los hombros
                y_min = min(left_shoulder_px[1], right_shoulder_px[1]) - 45  # Margen para comenzar desde un poco arriba de los hombros

            elif category == "cuello":

                # Calcular el ancho del collar en función de la distancia entre los extremos de la boca
                width = int(np.linalg.norm(np.array(mouth_right_px) - np.array(mouth_left_px)) * 3)  # Margen adicional

                # Calcular la altura como una proporción del ancho
                height = int(width * 1.0) 

                # Centrar el collar horizontalmente en función de la nariz
                x_min = int(nose_px[0] - width / 2)

                # Calcular posición vertical en base al hombro
                y_min = int( (left_shoulder_px[1] - nose_px[1]*0.24 )  ) 


            elif category == "cabeza":
                # Calcular el centro horizontal del rostro (entre las orejas)
                center_x = (ear_left_px[0] + ear_right_px[0]) // 2

                # Calcular el ancho del sombrero basado en la distancia entre las orejas
                ear_distance = np.linalg.norm(np.array(ear_right_px) - np.array(ear_left_px))
                width = int(ear_distance * 2.8)  # Margen adicional dinámico basado en la distancia

                # Calcular la altura del sombrero como una proporción del ancho
                height = int(width * 0.5)  # Relación típica de altura para un sombrero

                # Posicionar el sombrero centrado respecto al rostro
                x_min = center_x - width // 2  # Centrar horizontalmente
                y_min = ear_left_px[1] - height  # Posicionar encima de la cabeza

            # Redimensionar el ítem
            resized_item = cv2.resize(current_item, (width, height))

            # Superponer el ítem en el frame
            self.overlay_image(frame, resized_item, x_min, y_min)

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

    def change_item_in_category(self, category):
        """
        Cambia al siguiente ítem (ropa) dentro de una categoría específica.
        """
        if category in self.assets and self.assets[category]:
            self.current_indices[category] = (self.current_indices[category] + 1) % len(self.assets[category])


    def start_camera(self):
        """
        Inicia la cámara y muestra detecciones de pose con ropa superpuesta.
        Permite cambiar de ítems o categorías.
        """
        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Espejo Inteligente', cv2.WINDOW_NORMAL)

        # Categoría actual para el clic
        self.current_category = "torso"

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

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:  # Cambiar prenda al hacer clic izquierdo
                self.change_item_in_category(self.current_category)

        cv2.setMouseCallback('Espejo Inteligente', mouse_callback)

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Error al acceder a la cámara.")
                    break

                # Convertir la imagen a RGB para Mediapipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                landmarks = self.pose_model.process_frame(rgb_frame)

                # Dibujar ropa según las categorías
                if landmarks:
                    self.overlay_clothing(frame, landmarks, self.current_category)

                # Mostrar el resultado
                cv2.imshow('Espejo Inteligente', frame)

                # Detectar eventos para cambiar ropa o categorías
                key = cv2.waitKey(1)
                if key == ord('q') or cv2.getWindowProperty('Espejo Inteligente', cv2.WND_PROP_VISIBLE) < 1:
                    break
                elif key == ord('1'):  # Cambiar categoría a "cabeza"
                    self.current_category = "cabeza"
                elif key == ord('2'):  # Cambiar categoría a "cuello"
                    self.current_category = "cuello"
                elif key == ord('3'):  # Cambiar categoría a "torso"
                    self.current_category = "torso"
        except Exception as e:
            print(f"Error inesperado: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()