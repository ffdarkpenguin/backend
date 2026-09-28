# Modelo de Backend

Objetivo: criar um modelo de backend para ser seguido

Os backends sempre serão em python a menos que tenha uma enorme vantagem fazer noutra linguagem

estrutura básica:

```
repo/                             ← raiz do repositório
├── portal/                       ← pacote com nome do projeto (exemplo: portal)
│   ├── __init__.py
│   ├── conf.py                   ← configuração (no .gitignore)
│   ├── conf-exemplo.py           ← template versionado da configuração
│   ├── erros.py                  ← exceção base Erro + tipos do sistema
│   ├── dominio/                  ← classes de domínio (Pydantic), regra de negócio
│   │   ├── base.py               ← Base / ModeloBase (id int) / ModeloBaseOID (ObjectId)
│   │   └── usuario.py            ← UsuarioParam + UsuarioPG + UsuarioMongo
│   ├── servico/                  ← orquestração (sufixo _svc)
│   │   ├── usuario_sql_svc.py
│   │   └── usuario_mongo_svc.py
│   ├── repositorio/              ← persistência
│   │   ├── genericos.py          ← TypeVar dos crudes
│   │   ├── sql/                  ← Postgres (psycopg 3)
│   │   │   ├── crude.py
│   │   │   └── usuario_repo.py
│   │   └── no_sql/               ← Mongo (pymongo)
│   │       ├── crude.py
│   │       └── usuario_repo.py
│   ├── lib/                      ← funções puras (datas, etc.)
│   │   └── dh.py
│   ├── interface/                ← entrada do sistema
│   │   ├── rest/
│   │   │   ├── app.py
│   │   │   └── rota/
│   │   │       ├── usuario_rt.py
│   │   │       ├── caso_uso.py
│   │   │       └── trata_excecao.py
│   │   └── cli.py
│   └── bot/                      ← processos assíncronos
├── tests/
│   ├── e2e/                      ← sistema completo (Playwright, quando houver front)
│   ├── funcional/                ← funcionalidades pela interface REST
│   ├── integracao/
│   │   └── repositorio/          ← camadas contra banco real
│   └── unitario/
├── SQL/                          ← DDL versionado (nome do projeto: portal.sql)
├── docs/
├── pyproject.toml                ← config de ferramentas (isort)
├── requirements.txt              ← dependências de produção
├── requirements-dev.txt          ← dependências de desenvolvimento (inclui as de produção)
├── pytest.ini                    ← pythonpath = . / marker regressao
├── .flake8
└── README.md                     ← orientação de rename do pacote e execução
```

Regras da estrutura:
- pacote com nome do projeto
- imports: `from portal.dominio.usuario import Usuario`
- sem `src/`
- sem `pip install` do projeto
- roda da raiz com `PYTHONPATH=.`
- execução por caminho de arquivo: `python portal/servico/arq.py`
- singular em tudo:
  - pastas
  - tabelas
  - endpoints
  - arquivos

## Domínio:
Deve ter classes de domínio. Toda lógica de negócio deve ficar no dominio.
  - cria com pydantic
  - duas bases:
    - `ModeloBase` — `id: int` (SQL)
    - `ModeloBaseOID` — `id: ObjectId` (Mongo)
    - as duas herdam de `Base` (datas `criado_em` / `alterado_em`)
  - PK é `_id` nos dois bancos
  - FK é `id_coisa`
  - campo pydantic se chama `id` com alias `_id` (limitação: pydantic rejeita campo `_id`)
  - sem `__setattr__` mágico
  - params de endpoint moram no domínio:
    - param é a base de campos da entidade
    - entidade herda: `UsuarioPG(ModeloBase, UsuarioParam)`
    - entrada ≠ entidade (ex.: senha + confirmação) → `Base` da interseção
      - param soma os campos só-de-entrada
      - entidade soma os só-persistidos (ex.: hash)
      - serviço faz a travessia

## Serviço:
Orquestrador de funcionalidades.
  - funções-módulo (sufixo `_svc`)
  - instancia o repositório direto no corpo (sem injeção — teste usa monkeypatch)
  - monta a entidade a partir do param
  - chama funcao de dominio que faz o que precisa ser feito
  - Grava resultados
  - Devolve resposta
  - Gera excessão do sistema se algo der errado (controle de fluxo via exceção)
  - exceção sobe — serviço não captura

## Repositório:
  - basicamento suporta 2 tipos: sql (default: postgres / psycopg 3) e no_sql (default: mongo / pymongo)
  - sem ORM — SQL em f-string
  - todo repo tem um crud completo com typevar (`CrudeSQL[Modelo]` / `CrudeMongo[Modelo]`)
  - todo respositório depois disso vira uma extenção do crud.
  - métodos: `insere` / `insere_varios` / `busca_id` / `busca_filtro` / `lista` / `altera` / `remove_id` / `remove_filtro` / `limpa`
  - `altera(modelo, atualiza_alterado_em=True)` — flag `False` preserva valor posto na mão
  - `insere_varios` é tudo-ou-nada
  - vazio → `NaoEncontrado` · duplicado → `Duplicado` · update sem linha → `NaoAlterado`
  - conexão autocommit — transação explícita e rara
  - DDL versionado em `SQL/<projeto>.sql`

## Erros:
  - `erros.py` com base `Erro(msg)`
  - domínio / serviço / repositório lançam — só a fronteira captura
  - mapa REST:
    - `NaoEncontrado` → 200 `ok=false`
    - demais `Erro` → 400
    - `FalhaAutenticacao` → 401
    - `SemPermissao` → 403
    - não previsto → 500
    - `FalhaAPIExterna` → 502

## Libs:
  - arquivos de funções puras de manipulação de dados
  - simplificar gerar data e horas comuns no sistema (`dh.py` — fuso São Paulo)
  - etc

## Testes:
  - níveis:
    - `unitario` — isolado (domínio / serviço com fake + monkeypatch)
    - `integracao` — camada contra banco real
    - `funcional` — funcionalidade pela interface REST
    - `e2e` — sistema completo com front (Playwright — futuro)
  - TDD vermelho → verde sempre
  - banco de teste real (`portal_teste` no postgres e no mongo)
  - marker `regressao` para teste nascido de bug

## Interface:
  - cria as maneiras de conversar com sistema. Comuns: REST e CLI
  - REST:
      - API rest usando fastapi
      - envelope `{ok, msg, dados}` em toda resposta (sucesso e erro)
      - rota chama serviço e envelopa — sem banco na rota
      - 1 router por recurso (sufixo `_rt`)
      - Padrão VERBO ENDPOINT
      - POST cria
      - GET lista
      - GET `{id}` busca específico
      - PUT `{id}` altera
      - DELETE `{id}` excluir

      pode criar filhos:
      - POST `usuario/{id}/token` - cria token para o usuário `{id}`
  - CLI:
    - Argparse
    - Padrão comando params
      - -param: param obrigatório
      - --param: param opcional
  Interafaces sempre chamam serviços.


A maioria dos sistemas vai ter Backend a parte feito em vue.js usando framework quasar.


Preciso sair desta discussão com um modelo montado (toda estrtura) e um crude simples de cadastro de usuário funcionando com banco postgres e mongo

- Existe um mongo rodando em localhost que pode ser acessado sem sem credencial
- Existe um postgres que pode ser acessado em localhost com user ff e senha 123123. Senha do usuário postgres se necessário também é 123123
