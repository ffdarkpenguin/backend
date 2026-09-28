import psycopg
import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from portal import conf
from portal.interface.rest.app import app
from portal.repositorio.no_sql.indexa import indexa


@pytest.fixture(scope='session', autouse=True)
def bancos_de_teste():
    with open('SQL/portal.sql', encoding='utf-8') as arquivo:
        sql = arquivo.read()
    with psycopg.connect(conf.dsn_pg_teste, autocommit=True) as conexao:
        conexao.execute(sql)
    indexa(conf.banco_mongo_teste)


@pytest.fixture(autouse=True)
def aponta_para_bancos_de_teste(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(conf, 'dsn_pg', conf.dsn_pg_teste)
    monkeypatch.setattr(conf, 'banco_mongo', conf.banco_mongo_teste)


@pytest.fixture(autouse=True)
def dados_limpos():
    with psycopg.connect(conf.dsn_pg_teste, autocommit=True) as conexao:
        conexao.execute('TRUNCATE usuario RESTART IDENTITY')
    mongo = MongoClient(conf.conexao_mongo)
    mongo[conf.banco_mongo_teste].usuario.delete_many({})
    mongo.close()


@pytest.fixture
def cliente():
    return TestClient(app)


@pytest.fixture(params=['/usuario/sql', '/usuario/mongo'])
def prefixo(request: pytest.FixtureRequest) -> str:
    return request.param


def test_crud_completo_de_usuario(cliente: TestClient, prefixo: str):
    resposta = cliente.post(prefixo, json={'nome': 'Ana', 'email': 'ana@teste.com'})
    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo['ok'] is True
    criado = corpo['dados']
    assert criado['nome'] == 'Ana'
    assert criado['email'] == 'ana@teste.com'
    assert criado['ativo'] is True
    _id = criado['_id']

    resposta = cliente.get(prefixo)
    corpo = resposta.json()
    assert corpo['ok'] is True
    assert len(corpo['dados']) == 1

    resposta = cliente.get(f'{prefixo}/{_id}')
    corpo = resposta.json()
    assert corpo['ok'] is True
    assert corpo['dados']['nome'] == 'Ana'

    resposta = cliente.put(
        f'{prefixo}/{_id}', json={'nome': 'Ana Maria', 'email': 'ana@teste.com', 'ativo': False})
    corpo = resposta.json()
    assert corpo['ok'] is True
    assert corpo['dados']['nome'] == 'Ana Maria'
    assert corpo['dados']['ativo'] is False

    resposta = cliente.delete(f'{prefixo}/{_id}')
    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo['ok'] is True

    resposta = cliente.get(f'{prefixo}/{_id}')
    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo['ok'] is False


def test_busca_inexistente_devolve_200_ok_false(cliente: TestClient, prefixo: str):
    if prefixo == '/usuario/sql':
        _id = 999
    else:
        _id = '0123456789ab0123456789ab'
    resposta = cliente.get(f'{prefixo}/{_id}')
    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo['ok'] is False
    assert corpo['msg']


def test_email_duplicado_devolve_400(cliente: TestClient, prefixo: str):
    cliente.post(prefixo, json={'nome': 'Ana', 'email': 'ana@teste.com'})
    resposta = cliente.post(prefixo, json={'nome': 'Outra', 'email': 'ana@teste.com'})
    corpo = resposta.json()
    assert resposta.status_code == 400
    assert corpo['ok'] is False
