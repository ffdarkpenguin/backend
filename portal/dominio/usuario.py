from pydantic import BaseModel

from portal.dominio.base import ModeloBase, ModeloBaseOID


class UsuarioParam(BaseModel):
    nome: str
    email: str
    ativo: bool = True


class UsuarioPG(ModeloBase, UsuarioParam):
    ...


class UsuarioMongo(ModeloBaseOID, UsuarioParam):
    ...
