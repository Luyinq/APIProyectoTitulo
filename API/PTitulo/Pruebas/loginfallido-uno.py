import requests
import json

url = "https://luyinq.pythonanywhere.com/login/"
data = {
    "rut": "333333333",
    "contrasena": "6AnwoYlO"
}

response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 400

# Verificar que se recibió el mensaje esperado
assert "El usuario no existe" in response.text

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))

print(response_data['message'])