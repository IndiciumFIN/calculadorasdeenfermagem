# CKO — Manual da automação e recibo de execução (v1.0.1)

**Data:** 15/11/2026 · **EPIC:** [#74](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/74) · **PR de dados:** [#70](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/70)

## 1. O que já foi executado, com evidência

O workflow **CKO Curriculum and Market Read-only Audit**, incluído em `.github/workflows/cko-curriculum-market-audit.yml`, foi acionado pelo evento `pull_request` na branch W7 e concluiu com `success`.

- [Run GitHub Actions #43690945716](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43690945716)
- **8 testes de unidade / negativos PASS**; compilação do Python PASS; geração dos cinco arquivos PASS.
- [Artefato `cko-curriculum-market-43690945716`](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43690945716/artifacts/14152760887), checksum ZIP `361edaa46010604f01588b6b8b6f4e1bb05cef344d2c25cd306742624d6ab42d`.
- Métricas do log: **65 especialidades**, **34 anúncios** na amostra, **163 linhas de backlog** e **nenhum drift numérico de baseline**. `release_allowed=false`.
- O artefato GitHub Actions expira conforme retenção do workflow (14 dias); os **inputs, códigos, manifesto e recibo** são permanentes na branch, sujeita à política de preservação do repositório.

## 2. Defeito encontrado e corrigido durante a homologação inicial

Na execução inaugural, a leitura via `defaultdict[specialty_id]` inseriu chaves vazias para todas as 65 especialidades, gerando incorretamente `65/65` com anúncio e dois drifts de baseline. **Não foram inventados anúncios no catálogo**, apenas o cálculo agregado estava incorreto. A correção usa `by_spec.get(sid, [])`, sem mutação. Também foram adicionadas duas verificações de regressão que confrontam diretamente a contagem de especialidades com as linhas efetivamente não vazias.

**Prova:** primeiro run #43690829983 exibiu drift falso; commits `62caa146` e `3fe15111` corrigiram código e teste; [run #43690945716](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43690945716) mostrou `drift: {}` e 8 testes PASS.

## 3. Como o pipeline funciona

Lê manifestos e catálogos existentes na W7, **sem rede externa nem conexão ao banco**, valida IDs, classes de skills, hierarquia COFEN, links candidatos, campos de direitos e `NO_GO`. Deduplica exatamente IDs de vagas, agrupa por especialidade, e gera:

| Saída | Uso |
|---|---|
| `coverage.json` | métricas, status, drift, hashes de inputs e bloqueios |
| `specialty_matrix.csv` | 65 linhas com n de vagas, ligações candidatas a cursos e skills |
| `backlog.jsonl` | filas com status explícito e requisitos de correção |
| `status.md` | sumário legível da rodada |
| `run_manifest.json` | revisão processada, hashes, flags de release e arquivos |

As **163 entradas de backlog** são **candidatas a tarefas**, não 163 GitHub Issues nem 163 correções realizadas. Composição da rodada: 51 especialidades sem anúncio neste recorte, 7 com amostra rasa, 35 sem vínculo de programa neste inventário, 65 com semântica curricular pendente e 5 bloqueios P0 transversais.

## 4. Como executar

No GitHub Actions, abrir **CKO Curriculum and Market Read-only Audit** e consultar as execuções de PR/push. O workflow também oferece `workflow_dispatch` quando permitido pelas configurações da instância. Para rodar diretamente em checkout autorizado:

```sh
python -m unittest discover -s tests -p 'test_cko_curriculum_market_audit.py' -v
python scripts/cko_curriculum_market_audit.py --repo-root . --out-dir ./tmp/cko-audit --revision "$(git rev-parse HEAD)"
```

O comando grava apenas o diretório de saída de auditoria especificado; não escreve na base nem altera fontes originais.

**Observação importante:** o evento GitHub Actions `schedule` só executa workflows presentes na **branch padrão**. Embora a agenda diária esteja configurada no YAML, **ela ainda não roda por `schedule`** enquanto a PR #70 não passar gates e a alteração correspondente não for aprovada na `main`. Os eventos de **push e pull_request já foram verificados**.

Há também uma tarefa de acompanhamento configurada para rodadas diárias, a partir de **16/11/2026, 9h15 (America/Sao_Paulo)**, com instrução para conferir fontes e avançar trabalhos candidatos de forma segura, ou registrar `HOLD`. Trata-se de acompanhamento independente e **não de execução garantida de aprovações humanas**.

## 5. Regras de falha segura e governança

Se faltar input, ID for duplicado, código de skill não estiver cadastrado, URL ou classe estiver inválida, ou um gate de publicação for alterado para verdadeiro indevidamente, o script retorna falha. **Pendências humanas não são erros que o script deva “consertar” marcando PASS**: seguem no backlog.

O workflow tem apenas `contents: read`, sem segredos, permissão de issues/write, token Supabase, deploy, merge ou autorização para copyright/clinical publication. A main mantém os seus gates; a PR #70 segue com falhas nos invariantes canônicos preexistentes e `Gate Agregador` pendente. Sucesso do auditor **não** equivale à aprovação global da plataforma.

## 6. Regras para trabalho contínuo

- Usar [Issue #74](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/74) como EPIC central; **não fechar tarefas** sem link de evidência e critério de aceite real.
- Atualizar a base versionada por nova PR ou commit em branch de revisão, conforme regras; manter uma fonte/edição/identidade.
- Se houver alteração de denominação ou contagem COFEN, atualizar catálogo a partir de ato oficial, documentar delta e verificar impacto nos pré-requisitos, skills e conteúdo.
- Se fonte/licença mudar, deixar o objeto e seus derivados em `REVALIDATION_REQUIRED` até revisão. 
- Toda rodada deve gerar: diferença desde a versão anterior, ações executadas, testes, próxima WO e impeditivos clínicos/jurídicos.
- Nenhuma tarefa automática pode confirmar uma licença, assinatura clínica, aceitação editorial ou autorização de publicação por conta própria.

**Situação:** `AUDITORIA_AUTOMÁTICA_FUNCIONANDO`; `WORKFLOW_SCHEDULE_GITHUB_HOLD_MAIN`; `EPIC_EM_EXECUCAO`; `CLINICAL_PUBLICATION_NO_GO`.
