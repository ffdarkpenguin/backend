import psycopg
import pytest

from portal import conf, erros
from portal.dominio.usuario import UsuarioPG
from portal.lib import dh
from portal.repositorio.sql.usuario_repo import UsuarioRepo


@pytest.fixture(scope='session', autouse=True)
def esquema():
    with open('SQL/portal.sql', encoding='utf-8') as arquivo:
        sql = arquivo.read()
    with psycopg.connect(conf.dsn_pg_teste, autocommit=True) as conexao:
        conexao.execute(sql)


@pytest.fixture(autouse=True)
def tabela_limpa():
    with psycopg.connect(conf.dsn_pg_teste, autocommit=True) as conexao:
        conexao.execute('TRUNCATE usuario RESTART IDENTITY')


@pytest.fixture
def repo():
    return UsuarioRepo(dsn=conf.dsn_pg_teste)


def test_insere_gera_id_e_devolve_modelo(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    assert usuario.id == 1
    assert usuario.nome == 'Ana'
    assert usuario.email == 'ana@teste.com'
    assert usuario.ativo is True


def test_insere_email_duplicado_gera_duplicado(repo: UsuarioRepo):
    repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    with pytest.raises(erros.Duplicado):
        repo.insere(UsuarioPG(nome='Outra Ana', email='ana@teste.com'))


def test_busca_id_devolve_usuario_inserido(repo: UsuarioRepo):
    inserido = repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    buscado = repo.busca_id(inserido.id)
    assert buscado == inserido


def test_busca_id_inexistente_gera_nao_encontrado(repo: UsuarioRepo):
    with pytest.raises(erros.NaoEncontrado):
        repo.busca_id(999)


def test_lista_devolve_todos_em_ordem_de_id(repo: UsuarioRepo):
    repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    repo.insere(UsuarioPG(nome='Bia', email='bia@teste.com'))
    usuarios = repo.lista()
    assert len(usuarios) == 2
    assert usuarios[0].nome == 'Ana'
    assert usuarios[1].nome == 'Bia'


def test_lista_filtra_por_campo(repo: UsuarioRepo):
    repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    repo.insere(UsuarioPG(nome='Bia', email='bia@teste.com', ativo=False))
    usuarios = repo.lista(ativo=True)
    assert len(usuarios) == 1
    assert usuarios[0].nome == 'Ana'


def test_lista_vazia_gera_nao_encontrado(repo: UsuarioRepo):
    with pytest.raises(erros.NaoEncontrado):
        repo.lista()


def test_busca_filtro_devolve_um_modelo(repo: UsuarioRepo):
    repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    usuario = repo.busca_filtro(email='ana@teste.com')
    assert usuario.nome == 'Ana'


def test_busca_filtro_sem_correspondencia_gera_nao_encontrado(repo: UsuarioRepo):
    with pytest.raises(erros.NaoEncontrado):
        repo.busca_filtro(email='ninguem@teste.com')


def test_altera_persiste_campos(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    usuario.nome = 'Ana Maria'
    usuario.ativo = False
    alterado = repo.altera(usuario)
    assert alterado.nome == 'Ana Maria'
    assert alterado.ativo is False
    buscado = repo.busca_id(usuario.id)
    assert buscado.nome == 'Ana Maria'


def test_altera_atualiza_alterado_em_por_default(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    momento_insercao = usuario.alterado_em
    usuario.nome = 'Ana Maria'
    alterado = repo.altera(usuario)
    assert alterado.alterado_em > momento_insercao


def test_altera_com_flag_false_preserva_alterado_em(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    momento_insercao = usuario.alterado_em
    usuario.nome = 'Ana Maria'
    alterado = repo.altera(usuario, atualiza_alterado_em=False)
    assert alterado.alterado_em == momento_insercao


def test_altera_nao_toca_criado_em(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    original = usuario.criado_em
    usuario.criado_em = dh.agora()
    alterado = repo.altera(usuario)
    assert alterado.criado_em == original


def test_altera_id_inexistente_gera_nao_alterado(repo: UsuarioRepo):
    usuario = UsuarioPG(**{'_id': 999, 'nome': 'Ana', 'email': 'ana@teste.com'})
    with pytest.raises(erros.NaoAlterado):
        repo.altera(usuario)


def test_altera_para_email_duplicado_gera_duplicado(repo: UsuarioRepo):
    repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    usuario = repo.insere(UsuarioPG(nome='Bia', email='bia@teste.com'))
    usuario.email = 'ana@teste.com'
    with pytest.raises(erros.Duplicado):
        repo.altera(usuario)


def test_remove_id_apaga_o_usuario(repo: UsuarioRepo):
    usuario = repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    repo.remove_id(usuario.id)
    with pytest.raises(erros.NaoEncontrado):
        repo.busca_id(usuario.id)


def test_remove_id_inexistente_gera_nao_encontrado(repo: UsuarioRepo):
    with pytest.raises(erros.NaoEncontrado):
        repo.remove_id(999)


def test_remove_filtro_apaga_correspondentes_e_devolve_quantidade(repo: UsuarioRepo):
    repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com', ativo=False))
    repo.insere(UsuarioPG(nome='Bia', email='bia@teste.com', ativo=False))
    repo.insere(UsuarioPG(nome='Caio', email='caio@teste.com'))
    removidos = repo.remove_filtro(ativo=False)
    assert removidos == 2
    restantes = repo.lista()
    assert len(restantes) == 1
    assert restantes[0].nome == 'Caio'


def test_limpa_esvazia_a_tabela(repo: UsuarioRepo):
    repo.insere(UsuarioPG(nome='Ana', email='ana@teste.com'))
    repo.limpa()
    with pytest.raises(erros.NaoEncontrado):
        repo.lista()


def test_insere_varios_insere_todos(repo: UsuarioRepo):
    novos = [
        UsuarioPG(nome='Ana', email='ana@teste.com'),
        UsuarioPG(nome='Bia', email='bia@teste.com'),
    ]
    inseridos = repo.insere_varios(novos)
    assert len(inseridos) == 2
    assert inseridos[0].id == 1
    assert inseridos[1].id == 2
    assert len(repo.lista()) == 2


def test_insere_varios_com_duplicado_nao_insere_nada(repo: UsuarioRepo):
    novos = [
        UsuarioPG(nome='Ana', email='ana@teste.com'),
        UsuarioPG(nome='Ana de novo', email='ana@teste.com'),
    ]
    with pytest.raises(erros.Duplicado):
        repo.insere_varios(novos)
    with pytest.raises(erros.NaoEncontrado):
        repo.lista()
