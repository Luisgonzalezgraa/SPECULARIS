import sys
import os
import time
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer


class SmartMirrorApp(QMainWindow):
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
        self.add_camera_message_label()  # Agregar mensaje para el espejo

        # Actualizar clima y hora
        self.update_weather()
        self.update_time()

    def load_and_set_image(self):
        if not os.path.exists(self.image_path):
            print(f"Error: La imagen '{self.image_path}' no existe.")
            sys.exit(1)

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
        logo_path = os.path.join(os.path.dirname(__file__), "Specularis.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(200, 200, Qt.KeepAspectRatio)
            self.logo_label = QLabel(self)
            self.logo_label.setPixmap(logo_pixmap)
        else:
            self.logo_label = QLabel("Specularis", self)
            self.logo_label.setStyleSheet("color: white; font-size: 24px; background-color: transparent;")
        self.logo_label.setAlignment(Qt.AlignCenter)

    def add_camera_message_label(self):
        self.camera_message_label = QLabel("", self)
        self.camera_message_label.setStyleSheet("color: red; font-size: 20px; background-color: transparent;")
        self.camera_message_label.setAlignment(Qt.AlignCenter)
        self.camera_message_label.setVisible(False)  # Ocultar por defecto

    def add_buttons(self):
        camera_icon_path = os.path.join(os.path.dirname(__file__), "reflexion.png")

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

    def position_elements(self):
        self.weather_label.setGeometry(self.width() // 2 - 200, 10, 400, 50)
        self.clock_label.setGeometry(self.width() // 2 - 100, self.height() - 100, 200, 50)
        self.logo_label.setGeometry(self.width() // 2 - 100, self.height() // 2 - 100, 200, 200)
        self.camera_message_label.setGeometry(self.width() // 2 - 150, self.height() // 2 - 200, 300, 50)
        self.camera_button.setGeometry(20, self.height() // 2 - 60, 50, 50)

    def update_weather(self):
        weather = self.get_weather()
        self.weather_label.setText(weather)
        QTimer.singleShot(60000, self.update_weather)

    def get_weather(self, city="Santiago, CL"):
        api_key = "8855c91d9de2a2a20745632cc165679a"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        translations = {
            "clear sky": "cielo despejado",
            "few clouds": "pocas nubes",
            "scattered clouds": "nubes dispersas",
            "broken clouds": "nubes rotas",
            "shower rain": "lluvia ligera",
            "rain": "lluvia",
            "thunderstorm": "tormenta eléctrica",
            "snow": "nieve",
            "mist": "neblina",
        }
        try:
            response = requests.get(url)
            weather = response.json()
            if weather.get("cod") == 200:
                temp = weather["main"]["temp"]
                description = weather["weather"][0]["description"]
                translated_description = translations.get(description.lower(), description).capitalize()
                city_name = weather["name"]
                return f"{city_name}: {temp}°C, {translated_description}"
            else:
                return f"Error: {weather.get('message', 'Ciudad no encontrada')}"
        except Exception as e:
            print(f"Error obteniendo clima: {e}")
            return "Error obteniendo clima"

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.setText(current_time)
        QTimer.singleShot(1000, self.update_time)

    def launch_espejo_script(self):
        import subprocess
        self.camera_message_label.setText("Espejo iniciando...")
        self.camera_message_label.setVisible(True)
        QTimer.singleShot(2000, lambda: self.camera_message_label.setVisible(False))
        subprocess.Popen(["python", "espejo.py"])  # Inicia la cámara siempre al frente


def main():
    app = QApplication(sys.argv)
    image_path = os.path.join(os.path.dirname(__file__), "fondo2.jpg")
    main_window = SmartMirrorApp(image_path)
    main_window.showFullScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
