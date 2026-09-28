from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def envelopa(
        ok: bool = True, msg: str = '', dados: Any = None, status_code: int = 200) -> JSONResponse:
    conteudo = jsonable_encoder({'ok': ok, 'msg': msg, 'dados': dados})
    return JSONResponse(status_code=status_code, content=conteudo)
