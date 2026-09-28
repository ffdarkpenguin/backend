from typing import Any, Generic, Type
from zoneinfo import ZoneInfo

from bson import CodecOptions, ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from portal import conf, erros
from portal.lib import dh
from portal.repositorio.genericos import ModeloGenerico

OPCOES_FUSO = CodecOptions(tz_aware=True, tzinfo=ZoneInfo('America/Sao_Paulo'))


class CrudeMongo(Generic[ModeloGenerico]):

    def __init__(self, colecao: str, modelo: Type[ModeloGenerico],
                 conexao_string: str = '', banco: str = ''):
        self.nome_colecao = colecao
        self.modelo = modelo
        if not conexao_string:
            conexao_string = conf.conexao_mongo
        if not banco:
            banco = conf.banco_mongo
        self.cliente: MongoClient = MongoClient(conexao_string)
        self.colecao = self.cliente[banco].get_collection(colecao, codec_options=OPCOES_FUSO)

    def insere(self, modelo: ModeloGenerico) -> ModeloGenerico:
        dados = modelo.model_dump(by_alias=True)
        try:
            self.colecao.insert_one(dados)
        except DuplicateKeyError as ex:
            raise erros.Duplicado(str(ex))
        return self.busca_id(dados['_id'])

    nao_alterar = ['_id', 'criado_em']

    def altera(self, modelo: ModeloGenerico, atualiza_alterado_em: bool = True) -> ModeloGenerico:
        if atualiza_alterado_em:
            modelo.alterado_em = dh.agora()
        dados = modelo.model_dump(by_alias=True)
        _id = dados['_id']
        for campo in self.nao_alterar:
            dados.pop(campo)
        try:
            resultado = self.colecao.update_one({'_id': _id}, {'$set': dados})
        except DuplicateKeyError as ex:
            raise erros.Duplicado(str(ex))
        if not resultado.matched_count:
            raise erros.NaoAlterado(f'{self.nome_colecao}: _id {_id} não alterado')
        return self.busca_id(_id)

    def lista(self, **filtro: Any) -> list[ModeloGenerico]:
        documentos = self.colecao.find(filtro).sort('_id')
        modelos = [self.modelo(**documento) for documento in documentos]
        if not modelos:
            raise erros.NaoEncontrado(f'{self.nome_colecao}: nada encontrado')
        return modelos

    def busca_filtro(self, **filtro: Any) -> ModeloGenerico:
        documento = self.colecao.find_one(filtro)
        if not documento:
            raise erros.NaoEncontrado(f'{self.nome_colecao}: nada encontrado para {filtro}')
        return self.modelo(**documento)

    def insere_varios(self, modelos: list[ModeloGenerico]) -> list[ModeloGenerico]:
        inseridos: list[ModeloGenerico] = []
        try:
            for modelo in modelos:
                inseridos.append(self.insere(modelo))
        except erros.Duplicado:
            ids_inseridos = [inserido.id for inserido in inseridos]
            self.colecao.delete_many({'_id': {'$in': ids_inseridos}})
            raise
        return inseridos

    def remove_id(self, _id: ObjectId):
        resultado = self.colecao.delete_one({'_id': _id})
        if not resultado.deleted_count:
            raise erros.NaoEncontrado(f'{self.nome_colecao}: _id {_id} não encontrado')

    def remove_filtro(self, **filtro: Any) -> int:
        resultado = self.colecao.delete_many(filtro)
        return resultado.deleted_count

    def limpa(self):
        self.colecao.delete_many({})

    def busca_id(self, _id: ObjectId) -> ModeloGenerico:
        documento = self.colecao.find_one({'_id': _id})
        if not documento:
            raise erros.NaoEncontrado(f'{self.nome_colecao}: _id {_id} não encontrado')
        return self.modelo(**documento)
