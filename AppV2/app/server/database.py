import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATABASE_URL = f"sqlite:///{base_dir}/name.db"
Base = declarative_base()
#Tbl Users
class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    password = Column(String)
#Tbl Veiculs
class Veiculo(Base):
    __tablename__ = 'Veiculos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    veiculo_equip = Column(String, unique=True)
    placa = Column(String, unique=True)
#TBLforCodeAlterations
class CodigoAlteracao(Base):
    __tablename__ = 'CodigoAlteracoes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    placa = Column(String, ForeignKey('Veiculos.placa'))
    veiculo_equip_antigo = Column(String)
    veiculo_equip_novo = Column(String)
    data_alteracao = Column(DateTime)
#Tbl Abasteciments
class Abastecimento(Base):
    __tablename__ = 'Abastecimentos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    req = Column(String)
    requisitante = Column(String)
    km_atual = Column(Float)
    data_req = Column(DateTime)
    veiculo_equip = Column(String, ForeignKey('Veiculos.veiculo_equip'))
    litros = Column(Float)
    diferenca_de_km = Column(Float)
    litros_anterior = Column(Float)
    km_por_litro = Column(Float)
    veiculo = relationship("Veiculo", foreign_keys=[veiculo_equip], back_populates='abastecimentos')
# Updting Tbl Veiculs p/includ relacionament
Veiculo.abastecimentos = relationship("Abastecimento", order_by=Abastecimento.id, back_populates='veiculo')
#Tbl Avg_Km
class MediaKm(Base):
    __tablename__ = 'Media_Km'
    id = Column(Integer, primary_key=True, autoincrement=True)
    veiculo_equip = Column(String, ForeignKey('Veiculos.veiculo_equip'))
    media_km_por_litro = Column(Float)
    veiculo = relationship("Veiculo", foreign_keys=[veiculo_equip])
#Funç~ autenticatn d'user
def autenticar_usuario(username, password):
    usuario = session.query(User).filter_by(username=username, password=password).first()
    return usuario is not None
#Creatng t-engine doSQLAlchemy
engine = create_engine(DATABASE_URL)
#Creatng tbls
Base.metadata.create_all(engine)
#Creatng aNew sessão
Session = sessionmaker(bind=engine)
session = Session()