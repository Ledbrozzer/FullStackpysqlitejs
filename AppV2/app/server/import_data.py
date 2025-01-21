#app/server/import_data.py
import pandas as pd
import os
from sqlalchemy.orm import sessionmaker
from database import engine, User, Veiculo, Abastecimento, MediaKm
#Functn t/Lê arqvsExcel
def read_excel(file_path):
    try:
        return pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
#PathsT/Files(ajustConform Needd)
veiculo_file_path = r'C:\Users\m\D\R.xlsx'
abastecimento_file_path = r'C:\Users\l\D\C.xlsx'
def import_veiculos():
    veiculos_df = read_excel(veiculo_file_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    for _, row in veiculos_df.iterrows():
        veiculo = session.query(Veiculo).filter_by(placa=row['PLACA/']).first()
        if not veiculo:
            veiculo = Veiculo(
                veiculo_equip=row['Placa TOPCON'],
                placa=row['PLACA/']
            )
            session.add(veiculo)
        else:
            veiculo.veiculo_equip = row['Placa TOPCON']
    session.commit()
def import_abastecimentos():
    abastecimento_df = read_excel(abastecimento_file_path)
    abastecimento_df['Veículo/Equip.'] = abastecimento_df['Veículo/Equip.'].astype(str)
    abastecimento_df['Km Atual'] = pd.to_numeric(abastecimento_df['Km Atual'], errors='coerce')
    abastecimento_df['Data Req.'] = pd.to_datetime(abastecimento_df['Data Req.'], format='%d/%m/%Y', errors='coerce')
    abastecimento_df = abastecimento_df.sort_values(by=['Veículo/Equip.', 'Data Req.', 'Km Atual'])
    abastecimento_df['Diferença de Km'] = abastecimento_df.groupby('Veículo/Equip.')['Km Atual'].diff().abs().fillna(0)
    abastecimento_df['Litros Anterior'] = abastecimento_df.groupby('Veículo/Equip.')['Litros'].shift(1).fillna(0)
    abastecimento_df['Km por Litro'] = abastecimento_df['Diferença de Km'] / abastecimento_df['Litros Anterior']
    abastecimento_df['Km por Litro'] = abastecimento_df['Km por Litro'].round(3)
    Session = sessionmaker(bind=engine)
    session = Session()
    for _, row in abastecimento_df.iterrows():
        abastecimento = Abastecimento(
            req=row['Requisição'],
            requisitante=row['Requisitante'],
            km_atual=row['Km Atual'],
            data_req=row['Data Req.'],
            veiculo_equip=row['Veículo/Equip.'],
            litros=row['Litros'],
            diferenca_de_km=row['Diferença de Km'],
            litros_anterior=row['Litros Anterior'],
            km_por_litro=row['Km por Litro']
        )
        session.add(abastecimento)
    session.commit()
def calcular_media_km():
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(Abastecimento).order_by(Abastecimento.veiculo_equip).all()
    veiculos = {}
    for abastecimento in query:
        veiculo_equip = abastecimento.veiculo_equip
        if veiculo_equip not in veiculos:
            veiculos[veiculo_equip] = {'total_km': 0, 'total_litros': 0, 'num_abastecimentos': 0}
        veiculos[veiculo_equip]['total_km'] += abastecimento.diferenca_de_km or 0
        veiculos[veiculo_equip]['total_litros'] += abastecimento.litros_anterior or 0
        veiculos[veiculo_equip]['num_abastecimentos'] += 1
    for veiculo_equip, data in veiculos.items():
        media_km_por_litro = data['total_km'] / data['total_litros'] if data['total_litros'] != 0 else 0
        media_km = MediaKm(
            veiculo_equip=veiculo_equip,
            media_km_por_litro=media_km_por_litro
        )
        session.add(media_km)
    session.commit()
def criar_usuario(nome, senha):
    Session = sessionmaker(bind=engine)
    session = Session()
    novo_usuario = User(username=nome, password=senha)
    session.add(novo_usuario)
    session.commit()
if __name__ == "__main__":
    import_veiculos()
    import_abastecimentos()
    calcular_media_km()
    criar_usuario("Test User", "Test123") 
