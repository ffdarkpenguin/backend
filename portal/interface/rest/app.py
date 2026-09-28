from fastapi import FastAPI

from portal import erros
from portal.interface.rest.rota import usuario_rt
from portal.interface.rest.rota.trata_excecao import trata_excecao

app = FastAPI()
app.add_exception_handler(erros.Erro, trata_excecao)
app.add_exception_handler(Exception, trata_excecao)
app.include_router(usuario_rt.rota_sql)
app.include_router(usuario_rt.rota_mongo)
