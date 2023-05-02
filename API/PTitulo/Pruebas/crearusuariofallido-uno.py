import requests
import json

url = "https://luyinq.pythonanywhere.com/usuario/"
data = {
    "rut": "196178309",
    "contrasena": "Prueba1234",
    "nombre": "Juan",
    "apellido": "Perez",
    "correo": "lu.alegre@duocuc.cl",
    "celular": 945924700
}

response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 400

# Verificar que se recibió el mensaje esperado
assert "Bad Request" in response.text

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))
assert "message" in response_data

print(response_data['message'])
print(response_data['details'])