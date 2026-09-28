import pytest
from bson import ObjectId

from portal import erros
from portal.dominio.usuario import UsuarioMongo, UsuarioParam
from portal.servico import usuario_mongo_svc as svc


class FakeRepo:
    instancia = None

    def __init__(self):
        type(self).instancia = self
        self.chamadas = []

    def insere(self, usuario: UsuarioMongo) -> UsuarioMongo:
        self.chamadas.append(('insere', usuario))
        return usuario

    def busca_id(self, _id: ObjectId) -> UsuarioMongo:
        self.chamadas.append(('busca_id', _id))
        return UsuarioMongo(**{'_id': _id, 'nome': 'Ana', 'email': 'ana@teste.com'})

    def lista(self) -> list[UsuarioMongo]:
        self.chamadas.append(('lista',))
        usuario = UsuarioMongo(nome='Ana', email='ana@teste.com')
        return [usuario]

    def altera(self, usuario: UsuarioMongo) -> UsuarioMongo:
        self.chamadas.append(('altera', usuario))
        return usuario

    def remove_id(self, _id: ObjectId):
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
    assert isinstance(enviado.id, ObjectId)
    assert usuario == enviado


def test_busca_converte_string_para_object_id():
    oid = ObjectId()
    usuario = svc.busca(str(oid))
    assert FakeRepo.instancia.chamadas == [('busca_id', oid)]
    assert usuario.id == oid


def test_id_invalido_gera_id_invalido():
    with pytest.raises(erros.IdInvalido):
        svc.busca('nao-e-oid')


def test_lista_delega_ao_repo():
    usuarios = svc.lista()
    assert FakeRepo.instancia.chamadas == [('lista',)]
    assert len(usuarios) == 1


def test_altera_busca_aplica_params_e_grava():
    oid = ObjectId()
    params = UsuarioParam(nome='Ana Maria', email='novo@teste.com', ativo=False)
    usuario = svc.altera(str(oid), params)
    chamadas = FakeRepo.instancia.chamadas
    assert chamadas[0] == ('busca_id', oid)
    acao, gravado = chamadas[1]
    assert acao == 'altera'
    assert gravado.id == oid
    assert gravado.nome == 'Ana Maria'
    assert gravado.email == 'novo@teste.com'
    assert gravado.ativo is False
    assert usuario.nome == 'Ana Maria'


def test_remove_delega_ao_repo():
    oid = ObjectId()
    svc.remove(str(oid))
    assert FakeRepo.instancia.chamadas == [('remove_id', oid)]
