#Nesse arquivo teremos as configurações que usaremos no projeto
import os
from flask_sqlalchemy import SQLAlchemy
import googlemaps
from dotenv import load_dotenv
load_dotenv()


db = SQLAlchemy() # O objeto db é criado UMA ÚNICA VEZ aqui

API_KEY_BACK = os.getenv("API_KEY_GOOGLE_MAPS_BACK")
API_KEY = os.getenv("API_KEY_GOOGLE_MAPS")
#Api do google maps
if not API_KEY_BACK:
    raise EnvironmentError("A variável API_KEY_GOOGLE_MAPS_BACK não foi configurada.")

gmaps = googlemaps.Client(key=API_KEY_BACK)

