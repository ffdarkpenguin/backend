from typing import Any, Generic, Type

import psycopg
from psycopg.errors import UniqueViolation
from psycopg.rows import DictRow, dict_row

from portal import conf, erros
from portal.lib import dh
from portal.repositorio.genericos import ModeloGenerico


class CrudeSQL(Generic[ModeloGenerico]):

    nao_inserir = ['_id']
    nao_alterar = ['_id', 'criado_em']

    def __init__(self, tabela: str, modelo: Type[ModeloGenerico], dsn: str = ''):
        self.tabela = tabela
        self.modelo = modelo
        if dsn:
            self.dsn = dsn
        else:
            self.dsn = conf.dsn_pg
        self._conexao: psycopg.Connection[DictRow] | None = None

    @property
    def conexao(self) -> psycopg.Connection[DictRow]:
        if not self._conexao:
            self._conexao = psycopg.Connection.connect(
                self.dsn, autocommit=True, row_factory=dict_row)
        return self._conexao

    def insere(self, modelo: ModeloGenerico) -> ModeloGenerico:
        dados = modelo.model_dump(by_alias=True)
        for campo in self.nao_inserir:
            dados.pop(campo)
        campos = ', '.join(dados)
        marcadores = [f'%({campo})s' for campo in dados]
        valores = ', '.join(marcadores)
        sql = f'INSERT INTO {self.tabela} ({campos}) VALUES ({valores}) RETURNING *'
        try:
            linha = self._executa_e_le_um(sql, dados)
        except UniqueViolation as ex:
            raise erros.Duplicado(str(ex))
        return self.modelo(**linha)

    def insere_varios(self, modelos: list[ModeloGenerico]) -> list[ModeloGenerico]:
        with self.conexao.transaction():
            inseridos = [self.insere(modelo) for modelo in modelos]
        return inseridos

    def busca_id(self, _id: int) -> ModeloGenerico:
        sql = f'SELECT * FROM {self.tabela} WHERE _id = %(_id)s'
        linha = self._executa_e_le_um(sql, {'_id': _id})
        if not linha:
            raise erros.NaoEncontrado(f'{self.tabela}: _id {_id} não encontrado')
        return self.modelo(**linha)

    def altera(self, modelo: ModeloGenerico, atualiza_alterado_em: bool = True) -> ModeloGenerico:
        if atualiza_alterado_em:
            modelo.alterado_em = dh.agora()
        dados = modelo.model_dump(by_alias=True)
        campos_alteraveis = [campo for campo in dados if campo not in self.nao_alterar]
        atribuicoes = [f'{campo} = %({campo})s' for campo in campos_alteraveis]
        sets = ', '.join(atribuicoes)
        sql = f'UPDATE {self.tabela} SET {sets} WHERE _id = %(_id)s RETURNING *'
        try:
            linha = self._executa_e_le_um(sql, dados)
        except UniqueViolation as ex:
            raise erros.Duplicado(str(ex))
        if not linha:
            raise erros.NaoAlterado(f'{self.tabela}: _id {dados["_id"]} não alterado')
        return self.modelo(**linha)

    def lista(self, **filtro: Any) -> list[ModeloGenerico]:
        where, parametros = self._monta_where(filtro)
        sql = f'SELECT * FROM {self.tabela}{where} ORDER BY _id'
        with self.conexao.cursor() as cursor:
            cursor.execute(sql, parametros)  # type: ignore
            linhas = cursor.fetchall()
        if not linhas:
            raise erros.NaoEncontrado(f'{self.tabela}: nada encontrado')
        modelos = [self.modelo(**linha) for linha in linhas]
        return modelos

    def busca_filtro(self, **filtro: Any) -> ModeloGenerico:
        where, parametros = self._monta_where(filtro)
        sql = f'SELECT * FROM {self.tabela}{where}'
        linha = self._executa_e_le_um(sql, parametros)
        if not linha:
            raise erros.NaoEncontrado(f'{self.tabela}: nada encontrado para {filtro}')
        return self.modelo(**linha)

    def remove_id(self, _id: int):
        sql = f'DELETE FROM {self.tabela} WHERE _id = %(_id)s'
        with self.conexao.cursor() as cursor:
            cursor.execute(sql, {'_id': _id})  # type: ignore
            removidos = cursor.rowcount
        if not removidos:
            raise erros.NaoEncontrado(f'{self.tabela}: _id {_id} não encontrado')

    def remove_filtro(self, **filtro: Any) -> int:
        where, parametros = self._monta_where(filtro)
        sql = f'DELETE FROM {self.tabela}{where}'
        with self.conexao.cursor() as cursor:
            cursor.execute(sql, parametros)  # type: ignore
            return cursor.rowcount

    def limpa(self):
        sql = f'TRUNCATE {self.tabela} RESTART IDENTITY'
        with self.conexao.cursor() as cursor:
            cursor.execute(sql)  # type: ignore

    def _monta_where(self, filtro: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        if not filtro:
            return '', {}
        condicoes = [f'{campo} = %({campo})s' for campo in filtro]
        where = ' WHERE ' + ' AND '.join(condicoes)
        return where, filtro

    def _executa_e_le_um(self, sql: str, parametros: dict[str, Any]) -> dict[str, Any] | None:
        with self.conexao.cursor() as cursor:
            cursor.execute(sql, parametros)  # type: ignore
            return cursor.fetchone()
