from bson import ObjectId

from portal import erros
from portal.dominio.usuario import UsuarioMongo, UsuarioParam
from portal.repositorio.no_sql.usuario_repo import UsuarioRepo


def insere(params: UsuarioParam) -> UsuarioMongo:
    usuario = UsuarioMongo(**params.model_dump())
    return UsuarioRepo().insere(usuario)


def busca(_id: str) -> UsuarioMongo:
    return UsuarioRepo().busca_id(_para_oid(_id))


def lista() -> list[UsuarioMongo]:
    return UsuarioRepo().lista()


def altera(_id: str, params: UsuarioParam) -> UsuarioMongo:
    repo = UsuarioRepo()
    usuario = repo.busca_id(_para_oid(_id))
    for campo, valor in params.model_dump().items():
        setattr(usuario, campo, valor)
    return repo.altera(usuario)


def remove(_id: str):
    UsuarioRepo().remove_id(_para_oid(_id))


def _para_oid(_id: str) -> ObjectId:
    if not ObjectId.is_valid(_id):
        raise erros.IdInvalido(f'_id inválido: {_id}')
    return ObjectId(_id)
