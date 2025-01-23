import shelve
from dotenv import load_dotenv
import os
import time
import logging
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

marcador = 0

# def deduccion_llama(message):

#     interpretacion = ""

#     completion = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[
#             {
#             "role":"user",
#             "content":f"Interpreta la intención de este mensaje en una sola acción: {message}. Responde solamente con una palabra." 
#             }
#             ],
#         temperature=1,
#         max_tokens=1024,
#         top_p=1,
#         stream=True,
#         stop=None,
#     )

#     for chunk in completion:
#         if chunk.choices[0].delta.content != None and chunk.choices[0].delta.content != ".":
#             interpretacion += chunk.choices[0].delta.content

#     return interpretacion

def generate_response(message,indicador_mensajes,id=0):

    mensaje = ""
    data_info = ""
    
    if indicador_mensajes == 0:
        mensaje = """¡Hola! Bienvenido a Fotoclick 📸✨\nGracias por escribirnos. Somos expertos en capturar tus mejores momentos y ofrecerte artículos personalizados únicos para que siempre los lleves contigo. 🌄"""
        data_info = "Mensaje"
    
    elif indicador_mensajes == 1:
        data_info = "Menu"
    
    elif indicador_mensajes > 1:
        if id == 10:
            mensaje = "Encantados atenderte con camisetas."
            data_info = "Mensaje"
        
    return mensaje,data_info
    