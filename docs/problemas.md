# Problemas em aberto

## Acesso `_id` no Pydantic

- decidido: PK é `_id` nos dois bancos e FK é `id_coisa`
- pydantic não aceita campo começando com underscore (erro duro)
- o campo tem que se chamar `id` com alias `_id`
- no código o acesso fica `usuario.id`
- todo o resto fala `_id`:
  - banco
  - JSON
  - dump
  - shell
- opções:
  1. aceitar `usuario.id`
     - um único ponto de divergência
     - é como os projetos atuais fazem
  2. property `_id` com setter na base
     - `usuario._id` funciona para ler e escrever
     - as duas grafias passam a existir
     - repr e autocomplete mostram `id`
     - esquisitice a mais na base
- próximo passo: discutir com colega

## Uso de eventos

- padrão de eventos existe no bag5:
  - entidade acumula eventos numa lista interna
  - registry central explícito (`HANDLERS`) — olhando um evento vê tudo que acontece com ele
  - `processa(eventos)` consome e despacha
  - prefixos: `Ev` (fato que aconteceu) e `Cm` (intenção/comando)
- decidir:
  - entra no modelo padrão?
  - quando usar (critério de "domínio complexo o suficiente")
- próximo passo: discutir

## Depends do FastAPI

- banco via Depends está descartado
- rota chama serviço e serviço cuida da persistência
- sobrou decidir onde fica autenticação e transversais por requisição
- opções:
  1. Depends por rota
     - explícito na assinatura
     - varia por endpoint (público / protegido / papéis)
     - aparece no OpenAPI
     - substituível em teste
  2. classe de rota custom centralizada
     - zero ruído nas assinaturas
     - uniforme em tudo
     - invisível olhando a rota
     - variar por endpoint é desajeitado
- desempate: existe variação de exigência por endpoint nos sistemas reais?
- próximo passo: retomar quando houver código real de rota na frente
