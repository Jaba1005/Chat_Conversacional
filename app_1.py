import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv("GENAI_API_KEY")

# Inicializar el cliente
client = genai.Client(api_key=API_KEY)

configuration = types.GenerateContentConfig(
    max_output_tokens=2048,
    system_instruction="""Eres un asistente de un narrador de deportes. 
Tus respuestas deben ser concisas, teniendo presente que el usuario es un narrador de deportes.

Si te hacen una pregunta que no está realicionada con deportes, responde 'Lo siento, solo puedo responder preguntas relacionadas con temas relacionados a deportes. """
)

text = input("Escribe tu pregunta sobre deportes: ")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    config=configuration,
    contents=text
)
print(response.text)
