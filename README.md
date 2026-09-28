# Modelo de Backend

Modelo padrão de backend Python. Este repositório é a referência:

- estrutura
- convenções
- CRUD de usuário funcionando em Postgres e Mongo

## Começando um projeto novo

1. Renomear o pacote `portal/` para o nome do projeto (ex.: `vendas/`)
2. Imports no padrão: `from vendas.dominio.usuario import Usuario`
3. Executar sempre da raiz do repositório com `PYTHONPATH=.`
   - dev: `export PYTHONPATH=.` no bashrc
   - produção/Docker: `WORKDIR` na raiz + `ENV PYTHONPATH=.`
4. Sem `pip install` do projeto. Só dependências:
   - produção: `pip install -r requirements.txt`
   - desenvolvimento: `pip install -r requirements-dev.txt`

## Execução

- API: `uvicorn portal.interface.rest.app:app`
- Script por caminho de arquivo: `python portal/servico/arquivo.py`
- Testes: `pytest`

## Convenções

- Nomes no singular em tudo:
  - pastas
  - tabelas
  - endpoints
  - arquivos
- Camadas:
  - `dominio` — regra de negócio (Pydantic)
  - `servico` — orquestração (sufixo `_svc`)
  - `repositorio` — persistência (sufixo `_repo`)
  - `lib` — funções puras
  - `interface` — REST/CLI (rotas com sufixo `_rt`)
  - `bot` — processos assíncronos
- Fluxo:
  - interface chama serviço
  - serviço instancia o repositório que usa
  - exceção sobe até a fronteira REST que converte em resposta
