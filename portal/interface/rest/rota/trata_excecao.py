import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from portal import erros
from portal.interface.rest.rota.caso_uso import envelopa

logger = logging.getLogger(__name__)

STATUS_POR_ERRO = {
    erros.NaoEncontrado: 200,
    erros.FalhaAutenticacao: 401,
    erros.SemPermissao: 403,
    erros.FalhaAPIExterna: 502,
}


def trata_excecao(request: Request, excecao: Exception) -> JSONResponse:
    if isinstance(excecao, erros.Erro):
        status_code = STATUS_POR_ERRO.get(type(excecao), 400)
        return envelopa(ok=False, msg=excecao.msg, status_code=status_code)
    logger.error('falha interna', exc_info=excecao)
    return envelopa(ok=False, msg='falha interna', status_code=500)
