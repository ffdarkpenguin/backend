import pytest
from bson import ObjectId
from pydantic import ValidationError

from portal.dominio.usuario import UsuarioMongo, UsuarioParam, UsuarioPG


def test_usuario_pg_nasce_com_campos_e_id_int():
    usuario = UsuarioPG(nome='Ana', email='ana@teste.com')
    assert usuario.nome == 'Ana'
    assert usuario.email == 'ana@teste.com'
    assert usuario.ativo is True
    assert usuario.id == 0


def test_usuario_pg_exige_nome_e_email():
    with pytest.raises(ValidationError):
        UsuarioPG()


def test_usuario_param_aceita_campos_com_ativo_default():
    params = UsuarioParam(nome='Ana', email='ana@teste.com')
    assert params.nome == 'Ana'
    assert params.email == 'ana@teste.com'
    assert params.ativo is True


def test_usuario_param_exige_nome_e_email():
    with pytest.raises(ValidationError):
        UsuarioParam()


def test_usuario_mongo_nasce_com_campos_e_object_id():
    usuario = UsuarioMongo(nome='Ana', email='ana@teste.com')
    assert usuario.nome == 'Ana'
    assert usuario.email == 'ana@teste.com'
    assert usuario.ativo is True
    assert isinstance(usuario.id, ObjectId)
