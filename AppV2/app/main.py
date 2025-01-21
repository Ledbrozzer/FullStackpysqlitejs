import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))
from flask import Flask, request, render_template, redirect, url_for, jsonify, session as flask_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import extract
from datetime import datetime
from database import engine, autenticar_usuario, User, Abastecimento, Veiculo, MediaKm  #Certifify Tht'database.py'ISinPath'server'
import socket
app = Flask(__name__)
app.secret_key = ''
Session = sessionmaker(bind=engine)
session = Session()
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in flask_session:
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if autenticar_usuario(username, password):
            flask_session['username'] = username
            return redirect(url_for('main_page'))
        else:
            return "Login Falhou! Tente novamente."
    return render_template('login.html')
@app.route('/logout')
def logout():
    flask_session.pop('username', None)
    return redirect(url_for('login'))
@app.route('/main')
def main_page():
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    user = session.query(User).filter_by(username=flask_session['username']).first()
    return render_template('main.html', username=user.username) if user else redirect(url_for('login'))
@app.route('/alterar_senha', methods=['POST'])
def alterar_senha():
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    nova_senha = request.form['novaSenha']
    username = flask_session['username']
    user = session.query(User).filter_by(username=username).first()
    if user:
        user.password = nova_senha
        session.commit()
        return "Senha alterada com sucesso"
    return "Erro ao alterar a senha"
@app.route('/alterar_nome', methods=['POST'])
def alterar_nome():
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    novo_nome = request.form['novoNome']
    username = flask_session['username']
    user = session.query(User).filter_by(username=username).first()
    if user:
        user.username = novo_nome
        session.commit()
        flask_session['username'] = novo_nome  #Atualiz aSessão c/new nome
        return "Nome alterado com sucesso"
    return "Erro ao alterar o nome"
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    novo_username = request.form['username']
    nova_senha = request.form['password']
    user = User(username=novo_username, password=nova_senha)
    session.add(user)
    session.commit()
    return "Usuário cadastrado com sucesso"
@app.route('/deletar_conta', methods=['DELETE'])
def deletar_conta():
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    username = flask_session['username']
    user = session.query(User).filter_by(username=username).first()
    if user:
        session.delete(user)
        session.commit()
        flask_session.pop('username', None)
        return "Conta deletada com sucesso"
    return "Erro ao deletar a conta"
@app.route('/historico_veiculo', methods=['GET'])
def historico_veiculo():
    placa = request.args.get('placa')
    mes = request.args.get('mes')
    ano = request.args.get('ano')
    query = session.query(Abastecimento).join(Veiculo, Abastecimento.veiculo_equip == Veiculo.veiculo_equip)
    if placa:
        veiculo = session.query(Veiculo).filter_by(placa=placa).first()
        if veiculo:
            query = query.filter(Abastecimento.veiculo_equip == veiculo.veiculo_equip)
        else:
            return jsonify([])
    if mes and ano:
        query = query.filter(extract('month', Abastecimento.data_req) == int(mes)).filter(extract('year', Abastecimento.data_req) == int(ano))
    registros = query.all()
    historico = [
        {
            'placa': registro.veiculo_equip,
            'veiculo_equip': registro.veiculo_equip,
            'data_req': registro.data_req.strftime('%d/%m/%Y'),
            'km_atual': registro.km_atual,
            'litros': registro.litros,
            'diferenca_de_km': registro.diferenca_de_km,
            'litros_anterior': registro.litros_anterior,
            'km_por_litro': registro.km_por_litro,
        }
        for registro in registros
    ]
    return jsonify(historico)
@app.route('/procurar_abastecimento', methods=['GET'])
def procurar_abastecimento():
    placa = request.args.get('placa')
    mes = request.args.get('mes')
    ano = request.args.get('ano')
    if not placa or not mes or not ano:
        return jsonify([])  #Added t-verificatn t/camps nulls
    query = session.query(Abastecimento).join(Veiculo).filter(
        Veiculo.placa == placa,
        extract('month', Abastecimento.data_req) == int(mes),
        extract('year', Abastecimento.data_req) == int(ano)
    ).all()
    registros = [
        {
            'id': registro.id,
            'placa': registro.veiculo_equip,
            'veiculo_equip': registro.veiculo_equip,
            'data_req': registro.data_req.strftime('%d/%m/%Y'),
            'km_atual': registro.km_atual,
            'litros': registro.litros,
            'requisitante': registro.requisitante,
            'diferenca_de_km': registro.diferenca_de_km,
            'litros_anterior': registro.litros_anterior,
            'km_por_litro': registro.km_por_litro,
        }
        for registro in query
    ]
    return jsonify(registros)
@app.route('/abastecimento/<int:id>', methods=['GET'])
def obter_abastecimento(id):
    registro = session.query(Abastecimento).filter_by(id=id).first()
    if registro:
        return jsonify({
            'id': registro.id,
            'placa': registro.veiculo_equip,
            'veiculo_equip': registro.veiculo_equip,
            'data_req': registro.data_req.strftime('%d/%m/%Y'),
            'km_atual': registro.km_atual,
            'litros': registro.litros,
            'requisitante': registro.requisitante,
            'diferenca_de_km': registro.diferenca_de_km,
            'litros_anterior': registro.litros_anterior,
            'km_por_litro': registro.km_por_litro,
        })
    return "Registro não encontrado", 404
@app.route('/alterar_abastecimento', methods=['PUT'])
def alterar_abastecimento():
    data = request.get_json()
    id = data['id']
    nova_data_req = data['dataReq']
    novo_km_atual = data['kmAtual']
    novos_litros = data['litros']
    registro = session.query(Abastecimento).filter_by(id=id).first()
    if registro:
        registro.data_req = nova_data_req
        registro.km_atual = novo_km_atual
        registro.litros = novos_litros
        session.commit()
        return "Abastecimento alterado com sucesso"
    return "Erro ao alterar o abastecimento"
@app.route('/deletar_abastecimento/<int:id>', methods=['DELETE'])
def deletar_abastecimento(id):
    registro = session.query(Abastecimento).filter_by(id=id).first()
    if registro:
        session.delete(registro)
        session.commit()
        return "Abastecimento deletado com sucesso"
    return "Erro ao deletar o abastecimento"
@app.route('/abastecimento_anterior/<int:abastecimento_id>', methods=['GET'])
def abastecimento_anterior(abastecimento_id):
    registro_atual = session.query(Abastecimento).filter_by(id=abastecimento_id).first()
    if registro_atual:
        registro_anterior = session.query(Abastecimento).filter(
            Abastecimento.data_req < registro_atual.data_req,
            Abastecimento.veiculo_equip == registro_atual.veiculo_equip
        ).order_by(Abastecimento.data_req.desc()).first()
        if registro_anterior:
            return jsonify({
                'id': registro_anterior.id,
                'placa': registro_anterior.veiculo_equip,
                'veiculo_equip': registro_anterior.veiculo_equip,
                'data_req': registro_anterior.data_req.strftime('%d/%m/%Y'),
                'km_atual': registro_anterior.km_atual,
                'litros': registro_anterior.litros,
                'requisitante': registro_anterior.requisitante,
                'diferenca_de_km': registro_anterior.diferenca_de_km,
                'litros_anterior': registro_anterior.litros_anterior,
                'km_por_litro': registro_anterior.km_por_litro,
            })
        return "Não há registro anterior"
    return "Erro ao procurar abastecimento anterior"
@app.route('/consultar_media', methods=['GET'])
def consultar_media():
    placa = request.args.get('placa')
    veiculo = session.query(Veiculo).filter_by(placa=placa).first()
    if veiculo:
        media_km = session.query(MediaKm).filter_by(veiculo_equip=veiculo.veiculo_equip).first()
        if media_km:
            return jsonify({
                'veiculo_equip': media_km.veiculo_equip,
                'media_km_por_litro': round(media_km.media_km_por_litro, 2)
            })
    return jsonify({
        'veiculo_equip': '',
        'media_km_por_litro': 'Não encontrado'
    })
@app.route('/obter_veiculo_equip', methods=['GET'])
def obter_veiculo_equip():
    placa = request.args.get('placa')
    veiculo = session.query(Veiculo).filter_by(placa=placa).first()
    if veiculo:
        return jsonify({'veiculo_equip': veiculo.veiculo_equip})
    return jsonify({'veiculo_equip': 'Não encontrado'})
@app.route('/cadastrar_abastecimento', methods=['POST'])
def cadastrar_abastecimento():
    data = request.get_json()
    req = data['req']
    requisitante = data['requisitante']
    km_atual = float(data['kmAtual'])
    data_req = data['dataReq']
    veiculo_equip = data['veiculoEquip']
    placa = data['placa']
    litros = float(data['litros'])
    if not data_req:
        return jsonify({"error": "Campo de data_req é obrigatório"}), 400
    try:
        data_req = datetime.strptime(data_req, "%Y-%m-%d")  #Convert p/objet datetime
    except ValueError:
        return jsonify({"error": "Formato de data inválido"}), 400
    if not veiculo_equip and not placa:
        return jsonify({"error": "Campo de veiculo_equip ou placa é obrigatório"}), 400
    if placa:
        veiculo = session.query(Veiculo).filter_by(placa=placa).first()
        if veiculo:
            veiculo_equip = veiculo.veiculo_equip
        else:
            return jsonify({"error": "Placa não encontrada"}), 404
    #Lógic p/obtê abastecimentBefore
    abastecimento_anterior = session.query(Abastecimento).filter(
        Abastecimento.veiculo_equip == veiculo_equip,
        Abastecimento.data_req < data_req
    ).order_by(Abastecimento.data_req.desc()).first()
    diferenca_de_km = 0
    litros_anterior = 0
    km_por_litro = 0
    anomalia = False
    media_esperada = None
    if abastecimento_anterior:
        diferenca_de_km = km_atual - abastecimento_anterior.km_atual
        litros_anterior = abastecimento_anterior.litros
        km_por_litro = diferenca_de_km / litros if litros > 0 else 0
        #Verify if'km_por_litro'isBelow Average expectdFORvehículo
        media_km = session.query(MediaKm).filter_by(veiculo_equip=veiculo_equip).first()
        if media_km:
            media_esperada = media_km.media_km_por_litro
            if km_por_litro < media_esperada:
                anomalia = True
    #Insert newAbasteciment
    abastecimento = Abastecimento(
        req=req,
        requisitante=requisitante,
        km_atual=km_atual,
        data_req=data_req,
        veiculo_equip=veiculo_equip,
        litros=litros,
        diferenca_de_km=diferenca_de_km,
        litros_anterior=litros_anterior,
        km_por_litro=round(km_por_litro, 3)
    )
    try:
        session.add(abastecimento)
        session.commit()
        return jsonify({
            'message': "Abastecimento cadastrado com sucesso",
            'anomalia': anomalia,
            'mediaEsperada': media_esperada,
            'registroAtual': {
                'req': req,
                'requisitante': requisitante,
                'km_atual': km_atual,
                'data_req': data_req,
                'veiculo_equip': veiculo_equip,
                'litros': litros,
                'diferenca_de_km': diferenca_de_km,
                'litros_anterior': litros_anterior,
                'km_por_litro': round(km_por_litro, 3),
            },
            'abastecimentoAnterior': {
                'req': abastecimento_anterior.req,
                'requisitante': abastecimento_anterior.requisitante,
                'km_atual': abastecimento_anterior.km_atual,
                'data_req': abastecimento_anterior.data_req.strftime('%Y-%m-%d'),
                'veiculo_equip': abastecimento_anterior.veiculo_equip,
                'litros': abastecimento_anterior.litros,
                'diferenca_de_km': abastecimento_anterior.diferenca_de_km,
                'litros_anterior': abastecimento_anterior.litros_anterior,
                'km_por_litro': round(abastecimento_anterior.km_por_litro, 3) if abastecimento_anterior.km_por_litro else None
            } if abastecimento_anterior else None
        })
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Erro ao cadastrar abastecimento: {str(e)}"}), 500
#Funç p/obter IPprivad
def get_private_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip
@app.before_request
def limit_remote_addr():
    allowed_ips = ['192.168.', '10.', '172.16.', '172.31.']  #Subfaixs IPv4privads
    client_ip = request.remote_addr
    if not any(client_ip.startswith(ip) for ip in allowed_ips):
        return "Acesso não autorizado: você não está na rede Wi-Fi privada", 403
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5010, debug=True)