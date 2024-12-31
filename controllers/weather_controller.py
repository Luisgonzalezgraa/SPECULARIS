from PyQt5.QtCore import QTimer

class WeatherController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def update_weather(self, city="Santiago, CL"):
        """
        Obtiene el clima desde el modelo y actualiza la vista.
        """
        weather_data = self.model.get_weather(city)
        self.view.update_weather(weather_data)
        # Configurar para actualizar cada 60 segundos
        QTimer.singleShot(60000, lambda: self.update_weather(city))
