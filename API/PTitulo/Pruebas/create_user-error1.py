import requests
import json
import os

url = "http://127.0.0.1:8000/usuario/"
data = {
    "rut": "196178309",
    "contrasena": "Prueba1234",
    "nombre": "Juan",
    "apellido": "Perez",
    "correo": "lu.alegre@duocuc.cl",
    "celular": 945924700
}
file_name = os.path.basename(__file__)


response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 400

# Verificar que se recibió el mensaje esperado
def resultado():
    json_response = response.json()
    if "False" in json_response["success"]:
        return True
    else:
        return False

print(file_name, resultado())