import requests
import json
import os

url = "https://luyinq.pythonanywhere.com/usuario/"
data = {
    "rut": "80820690",
    "contrasena": "Prueba1234",
    "nombre": "Juan",
    "apellido": "Perez",
    "correo": "luyinnag@gmail.com",
    "celular": 945924701
}
file_name = os.path.basename(__file__)


response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 201

def resultado():
    json_response = response.json()
    if json_response["success"]:
        return True
    else:
        return False

print(file_name, resultado())