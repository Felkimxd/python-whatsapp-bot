import shelve
from dotenv import load_dotenv
import os
import time
import logging
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def deduccion_llama(message):
    
    json_fotoClick = {
        "Productos": [
            "Camisetas",
            {
                "Fotografias": {
                    "Tamaños": [
                        "4R",
                        "8R",
                        "6R",
                        "Pasaporte",
                        "Estados Unidos", 
                        "Europa",
                        "Carnet",
                        "Personalizado"
                    ]
                }
            },
            {
                "Jarros": ["Mágicos", "Normales"]
            },
            "Tarjetas"
        ],
        "Servicios": ["Retoques", "Montajes", "Restauracion_Fotografica"],
        "Pagos": ["Banco de Pinchincha", "Efectivo"],
        "Inexistencia":"Producto/Servicio Inexistente"
    }


    string_completion = ""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
            "role":"user",
            "content":f"Debes interpretar con este diccionario {json_fotoClick} lo que desea este mensaje {message}. Usa solamente palabras proporcionadas por el diccionario, ademas si no se puede interpretar con palabras del mismo, respondeme que es un servicio no disponible. Responde solamente con un diccionario con los requerimientos" 
            }
            ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    for chunk in completion:
        if chunk.choices[0].delta.content != None and chunk.choices[0].delta.content != ".":
            string_completion += chunk.choices[0].delta.content

    return string_completion


def generate_response(message):

    pass
