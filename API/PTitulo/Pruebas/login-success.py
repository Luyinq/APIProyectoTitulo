import requests
import json
import os

url = "http://127.0.0.1:8000/login/"
data = {
    "rut": "196178309",
    "contrasena": "Prueba123"
}
file_name = os.path.basename(__file__)

response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 200

def resultado():
    # Verificar que se recibió el mensaje esperado
    if "Inicio de sesión exitoso" in response.text:
        return True
    else:
        return False

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))
assert "data" in response_data

print(file_name, resultado())