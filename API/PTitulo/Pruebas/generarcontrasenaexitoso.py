import requests
import json

url = "https://luyinq.pythonanywhere.com/generar_password/"
data = {
    "rut": "80820690"
}

response = requests.post(url, data=data)

# Verificar el estado de la respuesta
assert response.status_code == 200

# Verificar que se recibió el mensaje esperado
assert "Se ha generado una nueva contraseña y se ha enviado por correo electrónico." in response.text

# Verificar que se recibieron los datos de usuario y token
response_data = json.loads(response.content.decode('utf-8'))
assert "message" in response_data

print(response_data['message'])