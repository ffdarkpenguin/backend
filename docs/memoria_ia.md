# memoria_ia — meu rascunho livre (usuario nunca le)

## FIM DA SESSAO 2026-09-27
- Usuario parou por hoje. Passo 5 implementado e apresentado mas NAO declarado fechado
  explicitamente — confirmar na retomada.
- Documentacao atualizada: backend.md (secoes Dominio/Servico/Repositorio/Erros/Libs/Testes/
  Interface refletem TODAS as decisoes; arvore com base.py, 2 svcs, conf-exemplo).
- problemas.md ganhou 3o ponto a pedido dele: USO DE EVENTOS (padrao bag5; decidir se entra
  no modelo e criterio de uso).
- Ele criou git no repo (perguntou como refazer commit inicial — respondi update-ref/amend).
  Git é dele, nao tocar.
- Ele trocou httpx->httpx2 no requirements-dev (warning do testclient sumiu; 74 passed).
- RETOMADA: (1) confirmar fechamento passo 5; (2) frentes restantes: CLI, bot/ (rascunho diz
  celery, nenhum projeto usa), problemas.md (_id property, Depends, eventos); (3) fase
  documentar do /discutir segue aberta ate ele alinhar que terminou.

## O que estamos fazendo
- /discutir sobre docs/backend.md. TIPO: tema (confirmado pelo usuario).
- Objetivo: definir modelo/padrao de backend Python reutilizavel, quase-definitivo.
- Sair da discussao com: estrutura montada + CRUD de cadastro de usuario funcionando em Postgres E Mongo.
- Fase atual: DISCUTIR (entender ja fechou).

## Infra dada pelo usuario
- Mongo em localhost, sem credencial.
- Postgres em localhost: user ff / senha 123123. Usuario postgres tambem 123123.

## Baseline convergente (bag5 + bot-moodle + padroes_dev) — provavelmente aceito
- Camadas: dominio, servico, repositorio, lib, interface (+ bots). Nomes em PT.
- Sufixos: _svc, _repo, _rt, _fix. dominio sem sufixo.
- Dominio em Pydantic v2, logica de negocio no dominio. Base com id alias '_id'.
- Servico orquestra, lanca excecao de dominio, nao captura.
- erros.py com base (ErroBag/Erro), handler central FastAPI mapeia p/ HTTP.
- CRUD generico Generic[Modelo], repos concretos finos estendem.
- FastAPI REST, 1 router por recurso, envelope {ok,msg,dados}.
- Drivers: pymongo (mongo) + psycopg3 (postgres). SEM ORM.
- Testes pytest, marker regressao. TDD com vermelho visivel (padroes_dev).

## Decisoes da discussao DI/repos (TODAS FECHADAS — usuario: "pode fechar com 6 pontos")
- Rota chama servico e envelopa; NENHUM banco na rota.
- Servico instancia UsuarioRepo() direto no corpo (legibilidade de dependencia pesou).
- Fachada global repo.* descartada.
- Teste via monkeypatch, sem cerimonia de injecao.
- Protocol: so onde funcao recebe repo como parametro; estreito/local se consumidor unico,
  compartilhado se 2+ reusam. Sem pasta de protocolos.
- Transacao multi-repo rara: explicita, conexao criada no servico que precisa.
- Trocar banco sem sistema saber = descartado pelo usuario ("ridiculo p/ sistema interligado").
- Conexoes autocommit; transacao explicita e rara.

## PENDENTE ANOTADO: acesso ._id no pydantic
- DEFINIDO: PK = _id nos dois bancos; FK = id_<coisa> (gramatica dele; _id = id de si mesmo).
  Motivos: uniformidade total (psql/mongosh/json/codigo), conflito com builtin id, sem
  mapeamento mental. Argumento do mongosh matou minha alternativa de mapear no CrudeMongo.
- ABERTO: pydantic nao aceita campo _id (erro duro). Opcoes na mesa: (a) aceitar usuario.id
  com alias; (b) property _id +setter na ModeloBase (duas grafias, repr mostra id).
  Usuario vai discutir com um colega. NAO fechar sozinho.

## PENDENTE ANOTADO: Depends
- Usuario achou a discussao abstrata demais; anotar como problema p/ depois.
- Estado: banco via Depends ja morreu; sobrou auth/transversais por requisicao.
  Questao aberta: auth por Depends por-rota vs APIRoute custom centralizada.
  Retomar quando houver codigo real de rota/auth na frente.

## Decisao alterado_em (FECHADA)
- Sem __setattr__ magico. Atualizacao explicita no altera() dos dois crudes.
- Assinatura: altera(modelo, atualiza_alterado_em=True) — NOME DA FLAG DEFINIDO PELO USUARIO
  (ele rejeitou 'carimba'; usar sempre 'atualiza'). Default True; False preserva o valor do modelo.
- insere() sem flag: default_factory + valor de fora preservado.

## ESTILO DOS ARQUIVOS DELE (README, docs, backend.md)
- Topicos e itens. Sem virgula onde puder. Sem texto corrido.
- Simplificado: sem funcoes, sem arquivos, sem citacoes (ja estava no prompt dele).
- Na MINHA memoria (este arquivo) eu escrevo como quiser — ele nao le.

## MODO DE TRABALHO (pedido do usuario)
- Discussao abstrata cansa; ele decide melhor VENDO CODIGO REAL.
- Seguir: montar o modelo concreto (estrutura + arquivos) e discutir os furos restantes
  em cima do codigo.

## Estado da construcao do modelo
- PASSO 1 FEITO: arvore portal/ + tests/ criada; erros.py (Erro, NaoEncontrado, Duplicado,
  NaoAlterado); requirements.txt + requirements-dev.txt (pedido do usuario); pytest.ini
  (pythonpath=., marker regressao); pyproject (isort 100); .flake8 (100); README (rename);
  desenho novo gravado em docs/backend.md (usuario: "ta melhor que o meu").
- VENV NAO EXISTE ainda; deps nao instaladas; instalacao é do usuario (regra: nunca instalar).
- PASSO 2 IMPLEMENTADO (13 passed, vermelho->verde): base.py (Base datas + ModeloBase id int
  + ModeloBaseOID ObjectId — DUAS bases, decisao do usuario: sem uniao, validacao estrita),
  usuario.py (UsuarioPG e UsuarioMongo no MESMO arquivo — nome dele), dh.py (agora() fuso SP).
  Rodar teste: `pytest` direto (venv no PATH; ele cobrou nao usar .venv/bin/pytest).
  Aguardando usuario declarar passo fechado.
- DEFINIDO: PK = coluna _id nos DOIS bancos (postgres inclusive).
  Motivos do usuario: base de dominio unica independente do banco; e variavel id em python
  sombreia o builtin id(). Pydantic: campo id com alias '_id' (campo literal _id nao pode,
  privado no pydantic).
  FALTA no passo 2: __setattr__ magico de alterado_em (bag5, inspect.stack — fragil/custoso,
  tem print esquecido) vs carimbo explicito; campos padrao da base; usuario.py.
- OBS: usuario editou backend.md por fora (mudou coisas, formatacao); linha do conf.py na
  arvore ainda diz 'sem segredo hardcoded' — contradiz decisao fechada; avisado.

## Furo CONFIG: FECHADO pelo usuario
- conf.py hardcoded SEM problema — padrao dele: conf.py no gitignore + conf-exemplo.py versionado.
- Nao re-questionar segredo hardcoded. env.py continua pro pouco que varia por ambiente.
- Docker: conf.py entra por mount/secret (avisado; ele sabe).
- .gitignore criado (conf.py, .venv, caches, settings.local.json).

## PASSO 3 FECHADO pelo usuario. Ajustes pos-fechamento que ele pediu:
- DDL na pasta SQL/ (MAIUSCULO, raiz do repo; ele renomeou na mao), arquivo = nome do projeto
  (SQL/portal.sql).
- Tipagem: Connection[DictRow] via psycopg.Connection.connect; ModeloGenerico bound=Base;
  type: ignore nas queries f-string (padrao dos crudes dele, 11x em cada projeto).
- PASSO 4 APROVADO: CrudeMongo + usuario_repo no_sql contra mongo real localhost.
  ATENCAO: mongo standalone NAO tem transacao — insere_varios tudo-ou-nada exige compensacao
  manual (deletar inseridos no erro). altera via $set (replace_one dropa campos). Datas mongo
  = ms + UTC: insere deve devolver o estado persistido (re-le apos gravar) p/ igualdade nos testes.
  Indice unique email: no_sql/indexa.py (padrao bag5), chamado na fixture de sessao.

## NIVEIS DE TESTE (redefinidos pelo usuario no passo 5)
- tests/e2e = SO Playwright sistema completo (front+back; e2e de verdade, futuro).
- tests/funcional/api = funcionalidades do backend pela interface REST (o que eu tinha
  chamado de e2e).
- tests/integracao/repositorio = camada contra banco real (repo nao é funcionalidade).
- tests/unitario = isolado.
- Envelope CONFIRMADO {ok,msg,dados}; mapa: NaoEncontrado->200 ok=false; Erro/validacao->400;
  FalhaAutenticacao->401; SemPermissao(novo)->403; interna->500; FalhaAPIExterna->502.
  Argumento dele que matou o 404 semantico: 404-rota vs 404-dado indistinguiveis = falso positivo.
- PASSO 5 IMPLEMENTADO (74 passed, topo verde): descida completa.
  - UsuarioParam no dominio = BASE DE CAMPOS; entidades herdam (ModeloBase, UsuarioParam).
    REGRA GERAL fechada: entrada==negocio -> param é base; entrada!=entidade (ex.: senha +
    confirmacao) -> nasce Base da intersecao, param soma os so-de-entrada, entidade os
    so-persistidos (hash), servico faz a travessia.
  - Servico: DOIS modulos (usuario_sql_svc / usuario_mongo_svc) — EU decidi ("resolve vc,
    conserto depois"); funcoes-modulo, UsuarioRepo() direto, mongo valida _id (IdInvalido).
    altera() aplica params via setattr loop.
  - erros novos: IdInvalido, FalhaAutenticacao, SemPermissao, FalhaAPIExterna.
  - rota/: caso_uso.envelopa, trata_excecao (mapa por tipo), usuario_rt (rota_sql/rota_mongo),
    app.py com handlers Erro+Exception.
  - Warning restante = deprecacao interna starlette/httpx, nao é nosso.
  - Testes de servico: fake com type(self).instancia = self + monkeypatch — padrao p/ repetir.
- Aguardando fechamento do passo 5. Faltam da agenda: CLI, bot/async (celery? nenhum projeto
  usa), fase DOCUMENTAR (backend.md secoes antigas desatualizadas, README), pendencias
  problemas.md (_id property, Depends).

## PASSO 4 IMPLEMENTADO (CrudeMongo) — aguardando fechamento
- 55 passed total. CrudeMongo mesma superficie do CrudeSQL; altera via $set; insere devolve
  estado persistido (re-le; mongo trunca datas p/ ms); insere_varios com COMPENSACAO manual
  (standalone sem transacao — avisado o residuo se processo morrer no meio); indexa.py com
  unique email; __init__.py nas pastas de teste (colisao de basename).
- PROXIMO (passo 5 a propor): usuario_svc (funcoes-modulo) — e ai vem envelope/rota depois.

## PASSO 3 IMPLEMENTADO (CrudeSQL) — historico

- 34 passed total; flake8+isort ok. Bancos portal e portal_teste criados no pg local
  (ff/123123; ja existiam portaldev/portalteste/portalteste_molde de outra coisa — nao tocar).
- CrudeSQL: insere, insere_varios (tudo-ou-nada via conexao.transaction()), busca_id,
  busca_filtro, lista (vazio->NaoEncontrado, padrao dos projetos dele), altera(flag
  atualiza_alterado_em), remove_id, remove_filtro, limpa. autocommit + dict_row, lazy conexao.
  UsuarioRepo(CrudeSQL[UsuarioPG]) tabela usuario. esquema.sql versionado (DROP+CREATE).
- Testes funcionais contra pg REAL banco portal_teste: esquema por sessao, TRUNCATE por teste,
  repo com dsn=conf.dsn_pg_teste explicito (sem monkeypatch).
- insere_varios simples tudo-ou-nada FOI DECISAO dele (sem modos do bag5).
- PROXIMO (passo 4): CrudeMongo no mesmo padrao + usuario_repo no_sql, contra mongo real
  localhost banco portal_teste.

## Furos abertos a decidir (agenda da discussao)
1. Packaging: pacote instalavel vs src no PYTHONPATH. Singular vs plural nos nomes (backend.md usa singular).
2. CRUD SQL/NoSQL: interface comum (Protocol/ABC) vs dois CRUDs paralelos duplicados.
3. REST: envelope + HTTP 200 pra erro esperado VS status HTTP real (REST estrito).
4. Config/segredos: Pydantic Settings + .env vs conf.py hardcoded.
5. DI: servico instancia repo vs injecao por Protocol/param (afeta teste).
6. Servico: funcoes-modulo vs classe.
7. Bots/async: backend.md diz celery, mas NENHUM projeto usa celery (bag5=asyncio, bot-moodle=selenium sync). Decidir de verdade.
8. Convencao id/_id ate no Postgres.
9. Testes: niveis e2e/funcional/unitario + banco real vs mock. Postgres/Mongo reais disponiveis.
10. CLI argparse: entra no baseline ou nao (nos 2 projetos esta stale/comentado).

## Decisoes fechadas
- Baseline convergente aceito sem contestacao (camadas PT, sufixos, pydantic v2 no dominio,
  servico orquestra e nao captura, erros.py + handler central, CRUD generico, FastAPI 1 router
  por recurso + envelope, pymongo + psycopg3 sem ORM, pytest + regressao + TDD vermelho visivel).
- Usuario trocou modelo p/ Fable 5 no meio; sem necessidade de reprocessar.
- FURO 1a (forma dos imports): DEFINIDO from projeto.pacote import ... (pacote top-level com
  nome do projeto; ex.: from portal.dominio import usuario). Copiavel-sem-rename nao importa;
  README orienta rename inicial. CUIDADO: discutir uma coisa por vez — usuario cobrou nao
  misturar forma do import com mecanica de resolucao.
- FURO 1b (mecanica): DEFINIDO. Pacote com nome do projeto direto na raiz do repo
  (repo/portal/dominio/...), eco aceito. SEM src/, SEM pip install do projeto (nem -e).
  PYTHONPATH=. (usuario ja tem no bashrc; prod/docker: WORKDIR + ENV PYTHONPATH).
  BASE do usuario: executar por caminho de arquivo (python portal/dominio/arq.py), sem -m.
  Docker/CI-CD: imagem por COPY + pip install so das deps (requirements.txt); imagem é o
  artefato; install do projeto sem lugar em dev nem prod.
- FURO 1c (nomenclatura): DEFINIDO singular em TUDO — pastas, tabelas, endpoints, arquivos.
  Motivo: mecanica sem flexao (derivacao por regra fixa, grep atravessa camadas).
  Historia: usuario carregava "tabela no singular" como verdade de um mentor antigo;
  convergiu que é escola, nao lei — o argumento real é a mecanica.
