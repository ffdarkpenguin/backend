from datetime import datetime
from typing import Annotated

from bson import ObjectId
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, PlainSerializer

from portal.lib import dh


def valida_object_id(valor: str | ObjectId) -> ObjectId:
    if not ObjectId.is_valid(valor):
        raise ValueError(f'ObjectId inválido: {valor}')
    return ObjectId(valor)


PydanticObjectId = Annotated[
    str | ObjectId, AfterValidator(valida_object_id), PlainSerializer(str, when_used='json')]


class Base(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    criado_em: datetime = Field(default_factory=dh.agora)
    alterado_em: datetime = Field(default_factory=dh.agora)


class ModeloBase(Base):
    id: int = Field(alias='_id', default=0)


class ModeloBaseOID(Base):
    id: PydanticObjectId = Field(alias='_id', default_factory=ObjectId)
