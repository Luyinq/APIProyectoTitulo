import requests
import json
import os

url = "https://luyinq.pythonanywhere.com/tipo_mascota/99999/"

# Retrieve the token from the Usuario model (replace with your actual query or ORM method)
headers = {
    "Authorization": "Token ef0fad5c167c39b1ed34477a76f821a068bd9b20"
}

file_name = os.path.basename(__file__)

response = requests.delete(url, headers=headers)

# Verificar el estado de la respuesta

def resultado():
    # Verificar que se recibió el mensaje esperado
    if response.status_code == 404:
        return True
    else:
        return False

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))

print(file_name, resultado())