import shelve
from dotenv import load_dotenv
import os
import time
import logging
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def generate_response(message):
    
    string_completion = ""
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
            "role":"user",
            "content":message 
            }
            ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    for chunk in completion:
        if chunk.choices[0].delta.content != None:
            string_completion += chunk.choices[0].delta.content
    
    return string_completion
