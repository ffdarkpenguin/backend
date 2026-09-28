from portal.dominio.usuario import UsuarioPG
from portal.repositorio.sql.crude import CrudeSQL


class UsuarioRepo(CrudeSQL[UsuarioPG]):

    def __init__(self, dsn: str = ''):
        super().__init__(tabela='usuario', modelo=UsuarioPG, dsn=dsn)
