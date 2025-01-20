# python -m venv env # env\Scripts\activate # python Server.py
#pip install flask sqlalchemy pandas openpyxl

# app/server/Server.py
from flask import Flask, request, jsonify, session as flask_session, redirect, url_for
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return "Servidor Local Configurado com Sucesso!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

def get_private_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

@app.before_request
def limit_remote_addr():
    allowed_ips = ['192.168.', '10.', '172.16.', '172.31.']  # Subfaixas IPv4 privadas
    client_ip = request.remote_addr
    if not any(client_ip.startswith(ip) for ip in allowed_ips):
        return "Acesso não autorizado: você não está na rede Wi-Fi privada", 403
