import time

import pytest
from bson import ObjectId
from pymongo import MongoClient

from portal import conf, erros
from portal.dominio.usuario import UsuarioMongo
from portal.lib import dh
from portal.repositorio.no_sql.indexa import indexa
from portal.repositorio.no_sql.usuario_repo import UsuarioRepo


@pytest.fixture(scope='session', autouse=True)
def indices():
    indexa(conf.banco_mongo_teste)


@pytest.fixture(autouse=True)
def colecao_limpa():
    cliente = MongoClient(conf.conexao_mongo)
    cliente[conf.banco_mongo_teste].usuario.delete_many({})
    cliente.close()


@pytest.fixture
def repo():
    return UsuarioRepo(banco=conf.banco_mongo_teste)


def test_insere_devolve_modelo_persistido(repo: UsuarioRepo):
    novo = UsuarioMongo(nome='Ana', email='ana@teste.com')
    usuario = repo.insere(novo)
    assert usuario.id == novo.id
    assert usuario.nome == 'Ana'
    assert usuario.email == 'ana@teste.com'
    assert usuario.ativo is True
    assert usuario.criado_em.tzinfo


def test_insere_email_duplicado_gera_duplicado(repo: UsuarioRepo):
    repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    with pytest.raises(erros.Duplicado):
        repo.insere(UsuarioMongo(nome='Outra Ana', email='ana@teste.com'))


def test_busca_id_devolve_usuario_inserido(repo: UsuarioRepo):
    inserido = repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    buscado = repo.busca_id(inserido.id)
    assert buscado == inserido


def test_busca_id_inexistente_gera_nao_encontrado(repo: UsuarioRepo):
    with pytest.raises(erros.NaoEncontrado):
        repo.busca_id(ObjectId())


def test_lista_devolve_todos_em_ordem_de_insercao(repo: UsuarioRepo):
    repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    repo.insere(UsuarioMongo(nome='Bia', email='bia@teste.com'))
    usuarios = repo.lista()
    assert len(usuarios) == 2
    assert usuarios[0].nome == 'Ana'
    assert usuarios[1].nome == 'Bia'


def test_lista_filtra_por_campo(repo: UsuarioRepo):
    repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    repo.insere(UsuarioMongo(nome='Bia', email='bia@teste.com', ativo=False))
    usuarios = repo.lista(ativo=True)
    assert len(usuarios) == 1
    assert usuarios[0].nome == 'Ana'


def test_lista_vazia_gera_nao_encontrado(repo: UsuarioRepo):
    with pytest.raises(erros.NaoEncontrado):
        repo.lista()


def test_busca_filtro_devolve_um_modelo(repo: UsuarioRepo):
    repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    usuario = repo.busca_filtro(email='ana@teste.com')
    assert usuario.nome == 'Ana'


def test_busca_filtro_sem_correspondencia_gera_nao_encontrado(repo: UsuarioRepo):
    with pytest.raises(erros.NaoEncontrado):
        repo.busca_filtro(email='ninguem@teste.com')


def test_altera_persiste_campos(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    usuario.nome = 'Ana Maria'
    usuario.ativo = False
    alterado = repo.altera(usuario)
    assert alterado.nome == 'Ana Maria'
    assert alterado.ativo is False
    buscado = repo.busca_id(usuario.id)
    assert buscado.nome == 'Ana Maria'


def test_altera_atualiza_alterado_em_por_default(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    momento_insercao = usuario.alterado_em
    time.sleep(0.005)
    usuario.nome = 'Ana Maria'
    alterado = repo.altera(usuario)
    assert alterado.alterado_em > momento_insercao


def test_altera_com_flag_false_preserva_alterado_em(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    momento_insercao = usuario.alterado_em
    usuario.nome = 'Ana Maria'
    alterado = repo.altera(usuario, atualiza_alterado_em=False)
    assert alterado.alterado_em == momento_insercao


def test_altera_nao_toca_criado_em(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    original = usuario.criado_em
    usuario.criado_em = dh.agora()
    alterado = repo.altera(usuario)
    assert alterado.criado_em == original


def test_altera_id_inexistente_gera_nao_alterado(repo: UsuarioRepo):
    usuario = UsuarioMongo(nome='Ana', email='ana@teste.com')
    with pytest.raises(erros.NaoAlterado):
        repo.altera(usuario)


def test_altera_para_email_duplicado_gera_duplicado(repo: UsuarioRepo):
    repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    usuario = repo.insere(UsuarioMongo(nome='Bia', email='bia@teste.com'))
    usuario.email = 'ana@teste.com'
    with pytest.raises(erros.Duplicado):
        repo.altera(usuario)


def test_remove_id_apaga_o_usuario(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    repo.remove_id(usuario.id)
    with pytest.raises(erros.NaoEncontrado):
        repo.busca_id(usuario.id)


def test_remove_id_inexistente_gera_nao_encontrado(repo: UsuarioRepo):
    with pytest.raises(erros.NaoEncontrado):
        repo.remove_id(ObjectId())


def test_remove_filtro_apaga_correspondentes_e_devolve_quantidade(repo: UsuarioRepo):
    repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com', ativo=False))
    repo.insere(UsuarioMongo(nome='Bia', email='bia@teste.com', ativo=False))
    repo.insere(UsuarioMongo(nome='Caio', email='caio@teste.com'))
    removidos = repo.remove_filtro(ativo=False)
    assert removidos == 2
    restantes = repo.lista()
    assert len(restantes) == 1
    assert restantes[0].nome == 'Caio'


def test_limpa_esvazia_a_colecao(repo: UsuarioRepo):
    repo.insere(UsuarioMongo(nome='Ana', email='ana@teste.com'))
    repo.limpa()
    with pytest.raises(erros.NaoEncontrado):
        repo.lista()


def test_insere_varios_insere_todos(repo: UsuarioRepo):
    novos = [
        UsuarioMongo(nome='Ana', email='ana@teste.com'),
        UsuarioMongo(nome='Bia', email='bia@teste.com'),
    ]
    inseridos = repo.insere_varios(novos)
    assert len(inseridos) == 2
    assert inseridos[0].id == novos[0].id
    assert inseridos[1].id == novos[1].id
    assert len(repo.lista()) == 2


def test_insere_varios_com_duplicado_nao_insere_nada(repo: UsuarioRepo):
    novos = [
        UsuarioMongo(nome='Ana', email='ana@teste.com'),
        UsuarioMongo(nome='Ana de novo', email='ana@teste.com'),
    ]
    with pytest.raises(erros.Duplicado):
        repo.insere_varios(novos)
    with pytest.raises(erros.NaoEncontrado):
        repo.lista()
