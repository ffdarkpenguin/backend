from pymongo import MongoClient

from portal import conf


def indexa(banco: str = ''):
    if not banco:
        banco = conf.banco_mongo
    cliente = MongoClient(conf.conexao_mongo)
    cliente[banco].usuario.create_index('email', unique=True)
    cliente.close()
