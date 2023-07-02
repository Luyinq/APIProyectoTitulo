import requests
import json
import os

url = "https://luyinq.pythonanywhere.com/tipo_mascota/"
data = {
    "nombre": "MascotaPrueba",
    "foto_1": "https://res.cloudinary.com/dfbon2wfu/image/upload/v1686510437/mascotas/22-foto_1.jpg",
    "foto_2": "",
    "tipo": 6,
    "dueno": "196178309",
}

# Retrieve the token from the Usuario model (replace with your actual query or ORM method)
headers = {
    "Authorization": "Token ef0fad5c167c39b1ed34477a76f821a068bd9b20"
}

file_name = os.path.basename(__file__)

response = requests.post(url, data=data, headers=headers)

# Verificar el estado de la respuesta
assert response.status_code == 201

def resultado():
    # Verificar que se recibió el mensaje esperado
    if response.status_code == 201:
        return True
    else:
        return False

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))
assert "data" in response_data

print(file_name, resultado())