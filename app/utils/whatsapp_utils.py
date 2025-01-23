import logging
from flask import current_app, jsonify
import json
import requests

from app.services.groq_service import generate_response
import re

mensajes_memoria = 0


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text, data_assign):

    boton_Ubicacion = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "location",
        "location": {
            "latitude": "0.34835031513615755",
            "longitude": "-78.12011524887379",
            "name": "Foto Click",
            "address": "Juan de Velasco 8-33 y José Joaquin de Olmedo",
        },
    }

    menu_interactivo = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "Escoja una opcion para ser atendido"},
            "body": {"text": "Servicios/Productos"},
            "footer": {"text": "Foto Click tú Solución"},
            "action": {
                "sections": [
                    {
                        "title": "Productos",
                        "rows": [
                            {
                                "id": "10",
                                "title": "Camisetas",
                                "description": "Camisetas personalizables",
                            },
                            {
                                "id": "5",
                                "title": "Jarros",
                                "description": "Jarros personalizables",
                            },
                        ],
                    }
                ],
                "button": "Escoja un producto",
            },
        },
    }
    mensaje_texto = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }

    if data_assign == "Mensaje":
        return json.dumps(mensaje_texto)
    elif data_assign == "Ubicacion":
        return json.dumps(boton_Ubicacion)
    elif data_assign == "Menu":
        return json.dumps(menu_interactivo)

    # return json.dumps(botones_inicio)

    #


# def generate_response(response):
#     # Return text in uppercase
#     return response.upper()


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):

    global mensajes_memoria

    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    context = body["entry"][0]["changes"][0]["value"]["messages"][0]['type']

    if context == 'text':
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        message_body = message["text"]["body"]  # ESTE ES EL MENSAJE QUE SE RECIBE DEL USUARIO

    elif context == 'interactive':
        message_body = ""
        id_interaccion = message = body["entry"][0]["changes"][0]["value"]["messages"][0]["interactive"]["list_reply"]["id"]
        interaccion_entera = int(id_interaccion)

    # TODO: implement custom function here

    if mensajes_memoria == 0:

        response, data_assign = generate_response(message_body, mensajes_memoria)
        data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response, data_assign)
        send_message(data)
        mensajes_memoria += 1
        message_body = ""
        response, data_assign = generate_response(message_body, mensajes_memoria)
        data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response, data_assign)
        send_message(data)
        mensajes_memoria += 1

    elif interaccion_entera == 10:
        message_body = ""
        response, data_assign = generate_response(
            message_body, mensajes_memoria, interaccion_entera)
        data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response, data_assign)
        send_message(data)


def send_followup_message(recipient_wa_id, message_body, indicador=None):
    """
    Envía un mensaje adicional al usuario de WhatsApp.

    Args:
        recipient_wa_id (str): ID de WhatsApp del destinatario.
        message_body (str): Contenido del mensaje a enviar.
        indicador (str, optional): Tipo de mensaje si se requiere personalización adicional.
    """
    # Prepara los datos del mensaje
    data = get_text_message_input(recipient_wa_id, message_body, indicador)

    # Envía el mensaje utilizando la función existente
    send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
