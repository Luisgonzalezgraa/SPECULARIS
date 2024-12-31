import os
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from models.weather_model import WeatherModel
from controllers.weather_controller import WeatherController

def main():
    app = QApplication([])

    # Ruta de la imagen de fondo
    image_path = os.path.join(os.path.dirname(__file__), "assets/images/fondo2.jpg")
    main_window = MainWindow(image_path)

    # Inicializar el modelo y el controlador del clima
    api_key = "8855c91d9de2a2a20745632cc165679a"  # Asegúrate de reemplazar esto con tu clave válida
    weather_model = WeatherModel(api_key)
    weather_controller = WeatherController(weather_model, main_window)

    # Actualizar el clima al inicio
    weather_controller.update_weather(city="Santiago, CL")

    # Mostrar la ventana principal
    main_window.showFullScreen()
    app.exec()

if __name__ == "__main__":
    main()
