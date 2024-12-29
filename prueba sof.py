import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import os
import cv2
import threading
import speech_recognition as sr
import requests
import time
from flask import Flask, request
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
import traceback

# Función para registrar errores en error.log dentro de la misma carpeta
def log_error():
    error_file_path = os.path.join(BASE_DIR, "error.log")
    with open(error_file_path, "w") as log_file:
        log_file.write(traceback.format_exc())

# Variables globales
cap = None
camera_thread = None
voice_thread = None
alexa_thread = None
camera_icon_global = None
mic_icon_global = None
feedback_label = None
app = Flask(__name__)  # Servidor Flask para Alexa
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuración de Alexa SDK
sb = SkillBuilder()

# Handlers de Alexa
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = "Hola, bienvenido a tu espejo inteligente."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

class WeatherIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("WeatherIntent")(handler_input)

    def handle(self, handler_input):
        weather = get_weather()
        speech_text = f"El clima actual es: {weather}"
        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

class CameraIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CameraIntent")(handler_input)

    def handle(self, handler_input):
        start_camera()
        speech_text = "La cámara ha sido activada."
        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

# Agregar handlers de Alexa
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(WeatherIntentHandler())
sb.add_request_handler(CameraIntentHandler())

@app.route("/", methods=["POST"])
def alexa_skill():
    return sb.lambda_handler()(request.get_json(force=True))

# Función para cargar un icono local
def get_icon(file_name, size=(50, 50)):
    try:
        file_path = os.path.join(BASE_DIR, file_name)
        icon = Image.open(file_path)
        icon = icon.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(icon)
    except Exception as e:
        print(f"Error cargando el icono {file_name}: {e}")
        return None

# Función para iniciar Alexa
def start_alexa():
    global alexa_thread
    if alexa_thread is None or not alexa_thread.is_alive():
        alexa_thread = threading.Thread(target=lambda: app.run(port=5000), daemon=True)
        alexa_thread.start()
        feedback_label.config(text="Alexa iniciada.", fg="green")
        print("Servidor Alexa iniciado en http://localhost:5000.")

# Función para obtener el clima
def get_weather(city="Santiago, CL"):
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
        return f"Error obteniendo clima: {str(e)}"

# Actualizaciones de reloj y clima
def update_weather():
    weather = get_weather()
    weather_label.config(text=weather)
    weather_label.after(60000, update_weather)

def update_time():
    current_time = time.strftime("%H:%M:%S")
    clock_label.config(text=current_time)
    clock_label.after(1000, update_time)

# Interfaz gráfica
root = tk.Tk()
root.title("Espejo Inteligente")
root.configure(background="black")
root.attributes("-fullscreen", True)

font_large = ("Helvetica", 48)
font_medium = ("Helvetica", 32)
font_small = ("Helvetica", 18)

clock_label = Label(root, font=font_large, bg="black", fg="white")
clock_label.pack(pady=20)

weather_label = Label(root, text="Cargando clima...", font=font_medium, bg="black", fg="white")
weather_label.pack(pady=20)

feedback_label = Label(root, text="", font=font_small, bg="black", fg="white")
feedback_label.pack(pady=20)

icon_frame = tk.Frame(root, bg="black")
icon_frame.place(relx=0.9, rely=0.5, anchor="center")

camera_icon_global = get_icon("reflexion.png")
mic_icon_global = get_icon("microfono-de-estudio.png")

camera_button = tk.Button(icon_frame, image=camera_icon_global, bg="black", command=lambda: print("Iniciar Cámara"), borderwidth=0)
camera_button.pack(pady=10)

mic_button = tk.Button(icon_frame, image=mic_icon_global, bg="black", command=lambda: print("Iniciar Micrófono"), borderwidth=0)
mic_button.pack(pady=10)

# Botón para iniciar Alexa
alexa_button = tk.Button(root, text="Iniciar Alexa", font=font_small, bg="black", fg="white", command=start_alexa)
alexa_button.place(relx=0.8, rely=0.9)

try:
    update_weather()
    update_time()
    root.mainloop()
except Exception:
    log_error()
    print("Se produjo un error. Revisa el archivo error.log para más detalles.")
