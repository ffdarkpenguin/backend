from fastapi import APIRouter
from fastapi.responses import JSONResponse

from portal.dominio.usuario import UsuarioParam
from portal.interface.rest.rota.caso_uso import envelopa
from portal.servico import usuario_mongo_svc, usuario_sql_svc

rota_sql = APIRouter(prefix='/usuario/sql', tags=['usuario sql'])
rota_mongo = APIRouter(prefix='/usuario/mongo', tags=['usuario mongo'])


@rota_sql.post('')
def cria_sql(params: UsuarioParam) -> JSONResponse:
    return envelopa(dados=usuario_sql_svc.insere(params))


@rota_sql.get('')
def lista_sql() -> JSONResponse:
    return envelopa(dados=usuario_sql_svc.lista())


@rota_sql.get('/{_id}')
def busca_sql(_id: int) -> JSONResponse:
    return envelopa(dados=usuario_sql_svc.busca(_id))


@rota_sql.put('/{_id}')
def altera_sql(_id: int, params: UsuarioParam) -> JSONResponse:
    return envelopa(dados=usuario_sql_svc.altera(_id, params))


@rota_sql.delete('/{_id}')
def remove_sql(_id: int) -> JSONResponse:
    usuario_sql_svc.remove(_id)
    return envelopa(msg='usuário removido')


@rota_mongo.post('')
def cria_mongo(params: UsuarioParam) -> JSONResponse:
    return envelopa(dados=usuario_mongo_svc.insere(params))


@rota_mongo.get('')
def lista_mongo() -> JSONResponse:
    return envelopa(dados=usuario_mongo_svc.lista())


@rota_mongo.get('/{_id}')
def busca_mongo(_id: str) -> JSONResponse:
    return envelopa(dados=usuario_mongo_svc.busca(_id))


@rota_mongo.put('/{_id}')
def altera_mongo(_id: str, params: UsuarioParam) -> JSONResponse:
    return envelopa(dados=usuario_mongo_svc.altera(_id, params))


@rota_mongo.delete('/{_id}')
def remove_mongo(_id: str) -> JSONResponse:
    usuario_mongo_svc.remove(_id)
    return envelopa(msg='usuário removido')
