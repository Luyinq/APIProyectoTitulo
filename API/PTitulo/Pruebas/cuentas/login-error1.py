import requests
import json
import os

url = "https://luyinq.pythonanywhere.com/login/"
data = {
    "rut": "333333333",
    "contrasena": "6AnwoYlO"
}
file_name = os.path.basename(__file__)

response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 400

# Verificar que se recibió el mensaje esperado
def resultado():
    if "El usuario no existe" in response.text:
        return True
    else:
        return False

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))

print(file_name, resultado())