from portal.dominio.usuario import UsuarioParam, UsuarioPG
from portal.repositorio.sql.usuario_repo import UsuarioRepo


def insere(params: UsuarioParam) -> UsuarioPG:
    usuario = UsuarioPG(**params.model_dump())
    return UsuarioRepo().insere(usuario)


def busca(_id: int) -> UsuarioPG:
    return UsuarioRepo().busca_id(_id)


def lista() -> list[UsuarioPG]:
    return UsuarioRepo().lista()


def altera(_id: int, params: UsuarioParam) -> UsuarioPG:
    repo = UsuarioRepo()
    usuario = repo.busca_id(_id)
    for campo, valor in params.model_dump().items():
        setattr(usuario, campo, valor)
    return repo.altera(usuario)


def remove(_id: int):
    UsuarioRepo().remove_id(_id)
