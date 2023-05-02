import requests
import json

url = "https://luyinq.pythonanywhere.com/usuario/"
data = {
    "rut": "80820690",
    "contrasena": "Prueba1234",
    "nombre": "Juan",
    "apellido": "Perez",
    "correo": "luyinnag@gmail.com",
    "celular": 945924701
}

response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 201

# Verificar que se recibió el mensaje esperado
assert "Usuario creado exitosamente." in response.text

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))
assert "message" in response_data

print(response_data['message'])