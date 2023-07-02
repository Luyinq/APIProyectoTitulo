import requests
import json
import os

url = "https://luyinq.pythonanywhere.com/generar_password/15/"
data = {
    "rut": "80820690"
}
file_name = os.path.basename(__file__)


response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 200

# Verificar que se recibió el mensaje esperado
def resultado():
    json_response = response.json()
    if json_response["success"]:
        return True
    else:
        return False

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))
assert "message" in response_data

print(file_name, resultado())