import requests

class WeatherModel:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.translations = {
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

    def get_weather(self, city="Santiago, CL"):
        """
        Obtiene datos del clima desde la API de OpenWeatherMap.
        """
        url = f"{self.base_url}?q={city}&appid={self.api_key}&units=metric"
        try:
            response = requests.get(url)
            weather = response.json()

            if weather.get("cod") == 200:
                temp = weather["main"]["temp"]
                description = weather["weather"][0]["description"]
                translated_description = self.translations.get(description.lower(), description).capitalize()
                city_name = weather["name"]

                return {
                    "city": city_name,
                    "temperature": temp,
                    "description": translated_description,
                }
            else:
                return {"error": weather.get("message", "Ciudad no encontrada")}
        except Exception as e:
            print(f"Error obteniendo clima: {e}")
            return {"error": "Error obteniendo clima"}
