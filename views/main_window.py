import time
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
import os

class MainWindow(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

        # Configuración de la ventana principal
        self.setWindowTitle("Espejo Inteligente")
        self.setGeometry(0, 0, 800, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Cargar imagen de fondo
        self.background_label = QLabel(self)
        self.load_and_set_image()

        # Crear elementos de la interfaz
        self.add_weather_label()
        self.add_clock_label()
        self.add_logo_label()
        self.add_buttons()
        self.add_camera_message_label()

        # Actualizar clima y hora
        self.update_time()
        
    def load_and_set_image(self):
        if not os.path.exists(self.image_path):
            print(f"Error: La imagen '{self.image_path}' no existe.")
            return

        pixmap = QPixmap(self.image_path)
        self.background_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding))
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setStyleSheet("background-color: transparent;")

        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.load_and_set_image()
        self.position_elements()

    def add_weather_label(self):
        self.weather_label = QLabel("Cargando clima...", self)
        self.weather_label.setStyleSheet("color: white; font-size: 18px; background-color: transparent;")
        self.weather_label.setAlignment(Qt.AlignCenter)

    def add_clock_label(self):
        self.clock_label = QLabel(self)
        self.clock_label.setStyleSheet("color: white; font-size: 48px; background-color: transparent;")
        self.clock_label.setAlignment(Qt.AlignCenter)

    def add_logo_label(self):
        # Construir la ruta desde el directorio raíz del proyecto
        project_root = os.path.dirname(os.path.dirname(__file__))  # Retrocede un nivel
        logo_path = os.path.join(project_root, "assets", "images", "Specularis.png")
        #print(f"Ruta del logo: {logo_path}")

        if os.path.exists(logo_path):
            # Cargar y ajustar el logo
            logo_pixmap = QPixmap(logo_path)
            if logo_pixmap.isNull():
                print("Error: No se pudo cargar el archivo de imagen.")
                self.logo_label = QLabel("Specularis", self)
                self.logo_label.setStyleSheet("color: white; font-size: 24px; background-color: transparent;")
            else:
                logo_pixmap = logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio)
                self.logo_label = QLabel(self)
                self.logo_label.setPixmap(logo_pixmap)
        else:
            print(f"Error: La imagen '{logo_path}' no existe.")
            self.logo_label = QLabel("Specularis", self)
            self.logo_label.setStyleSheet("color: white; font-size: 24px; background-color: transparent;")
        
        # Alinear el logo o texto
        self.logo_label.setAlignment(Qt.AlignCenter)

    def add_buttons(self):
        # Construir la ruta desde el directorio raíz del proyecto
        project_root = os.path.dirname(os.path.dirname(__file__))  # Retrocede un nivel
        camera_icon_path = os.path.join(project_root, "assets", "images", "reflexion.png")
        #print(f"Ruta del icono de la cámara: {camera_icon_path}")  # Depuración

        if os.path.exists(camera_icon_path):
            # Cargar y ajustar el icono
            camera_pixmap = QPixmap(camera_icon_path).scaled(50, 50, Qt.KeepAspectRatio)
            camera_icon = QIcon(camera_pixmap)
            self.camera_button = QPushButton(self)
            self.camera_button.setIcon(camera_icon)
            self.camera_button.setIconSize(camera_pixmap.size())
            self.camera_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent; 
                    border: none;
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 50);
                }
            """)
            self.camera_button.setGeometry(20, self.height() // 2 - 60, 50, 50)
            self.camera_button.setCursor(Qt.PointingHandCursor)
            self.camera_button.clicked.connect(self.launch_espejo_script)
        else:
            print(f"Error: La imagen '{camera_icon_path}' no existe.")

        
    def position_elements(self):
        self.weather_label.setGeometry(self.width() // 2 - 200, 10, 400, 50)
        self.clock_label.setGeometry(self.width() // 2 - 100, self.height() - 100, 200, 50)
        self.logo_label.setGeometry(self.width() // 2 - 100, self.height() // 2 - 100, 200, 200)
        self.camera_message_label.setGeometry(self.width() // 2 - 150, self.height() // 2 - 200, 300, 50)
        self.camera_button.setGeometry(20, self.height() // 2 - 60, 50, 50)    

    def add_camera_message_label(self):
        self.camera_message_label = QLabel("", self)
        self.camera_message_label.setStyleSheet("color: red; font-size: 20px; background-color: transparent;")
        self.camera_message_label.setAlignment(Qt.AlignCenter)
        self.camera_message_label.setVisible(False)  # Ocultar por defecto

    def update_weather(self, weather_data):
        """
        Actualiza la etiqueta del clima en la vista.
        """
        if "error" in weather_data:
            self.weather_label.setText(f"Error: {weather_data['error']}")
        else:
            self.weather_label.setText(
                f"{weather_data['city']}: {weather_data['temperature']}°C, {weather_data['description']}"
            )

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.setText(current_time)
        QTimer.singleShot(1000, self.update_time)
        
    def launch_espejo_script(self):
        from controllers.pose_controller import PoseController
        # Lista de rutas de imágenes de ropa
        polera_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "clothes", "polera_negra.png"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "clothes", "polera.png"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "clothes", "poleron_azul.png")
        ]

        # Crear instancia de PoseController con la lista de rutas
        self.pose_controller = PoseController(polera_paths)

        # Mostrar mensaje de inicio
        self.camera_message_label.setText("Espejo iniciando...")
        self.camera_message_label.setVisible(True)
        QTimer.singleShot(2000, lambda: self.camera_message_label.setVisible(True))

        # Iniciar la cámara
        self.pose_controller.start_camera()
