import requests
import json

url = "https://luyinq.pythonanywhere.com/login/"
data = {
    "rut": "196178309",
    "contrasena": "6AnwoYlO"
}

response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 200

# Verificar que se recibió el mensaje esperado
assert "Inicio de sesión exitoso" in response.text

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))
assert "data" in response_data

print(response_data['message'])