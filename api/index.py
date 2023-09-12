from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time


app = Flask(__name__)
CORS(app)

rota = 'https://amb-homolog.vercel.app/api/Agent'
access_token = None
token_expiration_time = 0

# Função para obter o token de acesso
def obter_token_de_acesso():
    global access_token
    global token_expiration_time

    # Verifique se o token atual está presente e ainda é válido
    if access_token and time.time() < token_expiration_time:
        return access_token

    # Se o token não existe ou está expirado, faça o login para obter um novo token
    login_url = 'https://amb-homolog.vercel.app/api/Identity/get-token'
    login_data = {
        "username": "admin",
        "password": "1234"
    }
    response = requests.get(url=login_url, json=login_data)

    if response.status_code == 200:
        # Extraia o novo token de acesso e seu tempo de expiração do JSON de resposta
        token_data = response.json()
        access_token = token_data.get('access_token')
        token_expiration_time = time.time() + token_data.get('expires_in')

        # Imprima o novo token de acesso e seu tempo de expiração
        print(f"Novo Token de Acesso: {access_token}")
        print(f"Tempo de Expiração do Token: {token_expiration_time}")

        return access_token
    else:
        raise Exception("Falha ao obter o token de acesso")

@app.route('/')
def home():
    return 'API'

@app.route('/http_for_https', methods=['POST'])
def http():
    if request.is_json:
        data = request.get_json()
        
        # Verifique a presença de cada chave individualmente
        if 'external_reference' in data and 'status' in data and 'name' in data \
                and 'birth_date' in data and 'gender' in data \
                and 'position_external_id' in data and 'shift_name' in data \
                and 'sector_external_id' in data and 'external_id' in data:

            # Atribua os valores a variáveis
            external_reference = data['external_reference']
            status = data['status']
            name = data['name']
            birth_date = data['birth_date']
            gender = data['gender']
            position_external_id = data['position_external_id']
            shift_name = data['shift_name']
            sector_external_id = data['sector_external_id']
            external_id = data['external_id']

            # Obtenha o token de acesso
            authorization_key = obter_token_de_acesso()

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {authorization_key}"
            }

            # Mensagem de registro para verificar se os dados estão sendo enviados corretamente
            print(f"Enviando dados para {rota}: {data}")

            # Corrija a solicitação HTTP POST para enviar dados como JSON
            outra_resposta = requests.post(url=rota, json=data, verify=False, headers=headers)

            # Mensagem de registro para verificar a resposta
            print(f"Resposta recebida: {outra_resposta.status_code}, {outra_resposta.text}")

            return outra_resposta.text, outra_resposta.status_code
        else:
            return jsonify({'erro': 'Dados incompletos'}), 400
    else:
        return jsonify({'erro': 'Requisição não é JSON'}), 400
