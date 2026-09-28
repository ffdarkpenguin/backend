import pytest

from portal.dominio.usuario import UsuarioParam, UsuarioPG
from portal.servico import usuario_sql_svc as svc


class FakeRepo:
    instancia = None

    def __init__(self):
        type(self).instancia = self
        self.chamadas = []

    def insere(self, usuario: UsuarioPG) -> UsuarioPG:
        self.chamadas.append(('insere', usuario))
        return usuario.model_copy(update={'id': 1})

    def busca_id(self, _id: int) -> UsuarioPG:
        self.chamadas.append(('busca_id', _id))
        return UsuarioPG(**{'_id': _id, 'nome': 'Ana', 'email': 'ana@teste.com'})

    def lista(self) -> list[UsuarioPG]:
        self.chamadas.append(('lista',))
        usuario = UsuarioPG(**{'_id': 1, 'nome': 'Ana', 'email': 'ana@teste.com'})
        return [usuario]

    def altera(self, usuario: UsuarioPG) -> UsuarioPG:
        self.chamadas.append(('altera', usuario))
        return usuario

    def remove_id(self, _id: int):
        self.chamadas.append(('remove_id', _id))


@pytest.fixture(autouse=True)
def instala(monkeypatch: pytest.MonkeyPatch):
    FakeRepo.instancia = None
    monkeypatch.setattr(svc, 'UsuarioRepo', FakeRepo)


def test_insere_monta_entidade_do_param_e_devolve_persistido():
    params = UsuarioParam(nome='Ana', email='ana@teste.com')
    usuario = svc.insere(params)
    acao, enviado = FakeRepo.instancia.chamadas[0]
    assert acao == 'insere'
    assert enviado.nome == 'Ana'
    assert enviado.email == 'ana@teste.com'
    assert enviado.id == 0
    assert usuario.id == 1


def test_busca_delega_ao_repo():
    usuario = svc.busca(5)
    assert FakeRepo.instancia.chamadas == [('busca_id', 5)]
    assert usuario.id == 5


def test_lista_delega_ao_repo():
    usuarios = svc.lista()
    assert FakeRepo.instancia.chamadas == [('lista',)]
    assert len(usuarios) == 1


def test_altera_busca_aplica_params_e_grava():
    params = UsuarioParam(nome='Ana Maria', email='novo@teste.com', ativo=False)
    usuario = svc.altera(5, params)
    chamadas = FakeRepo.instancia.chamadas
    assert chamadas[0] == ('busca_id', 5)
    acao, gravado = chamadas[1]
    assert acao == 'altera'
    assert gravado.id == 5
    assert gravado.nome == 'Ana Maria'
    assert gravado.email == 'novo@teste.com'
    assert gravado.ativo is False
    assert usuario.nome == 'Ana Maria'


def test_remove_delega_ao_repo():
    svc.remove(5)
    assert FakeRepo.instancia.chamadas == [('remove_id', 5)]
