from portal.dominio.usuario import UsuarioMongo
from portal.repositorio.no_sql.crude import CrudeMongo


class UsuarioRepo(CrudeMongo[UsuarioMongo]):

    def __init__(self, conexao_string: str = '', banco: str = ''):
        super().__init__(
            colecao='usuario', modelo=UsuarioMongo, conexao_string=conexao_string, banco=banco)
