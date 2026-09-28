from datetime import datetime

import pytest
from bson import ObjectId
from pydantic import ValidationError

from portal.dominio.base import ModeloBase, ModeloBaseOID


def test_modelo_base_tem_id_zero_por_default():
    modelo = ModeloBase()
    assert modelo.id == 0


def test_modelo_base_aceita_id_pelo_alias():
    modelo = ModeloBase(**{'_id': 5})
    assert modelo.id == 5


def test_modelo_base_datas_nascem_preenchidas_com_timezone():
    modelo = ModeloBase()
    assert isinstance(modelo.criado_em, datetime)
    assert isinstance(modelo.alterado_em, datetime)
    assert modelo.criado_em.tzinfo
    assert modelo.alterado_em.tzinfo


def test_modelo_base_preserva_data_vinda_de_fora():
    data = datetime(2020, 1, 2, 3, 4, 5)
    modelo = ModeloBase(criado_em=data)
    assert modelo.criado_em == data


def test_modelo_base_dump_usa_alias_id():
    modelo = ModeloBase(**{'_id': 7})
    dump = modelo.model_dump(by_alias=True)
    assert dump['_id'] == 7
    assert 'id' not in dump


def test_modelo_base_oid_nasce_com_object_id():
    modelo = ModeloBaseOID()
    assert isinstance(modelo.id, ObjectId)


def test_modelo_base_oid_aceita_string_de_object_id():
    oid = ObjectId()
    modelo = ModeloBaseOID(**{'_id': str(oid)})
    assert modelo.id == oid


def test_modelo_base_oid_rejeita_id_invalido():
    with pytest.raises(ValidationError):
        ModeloBaseOID(**{'_id': 'nao-e-oid'})


def test_modelo_base_oid_dump_json_vira_string():
    modelo = ModeloBaseOID()
    dump = modelo.model_dump(mode='json', by_alias=True)
    assert dump['_id'] == str(modelo.id)
