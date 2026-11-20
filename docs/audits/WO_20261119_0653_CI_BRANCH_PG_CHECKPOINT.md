# CE / CKO / NCOS — checkpoint 2026-11-19 06:53 BRT

## Origem, escopo e integridade
Último checkpoint consultado: `WO_20261119_0552_CONSTRAINT_CROSSWALK_CHECKPOINT.md`, blob `1a86852bc8909b6dda86b4278791510434ce7c9b`, commit anterior informado `01c7055c4f6b853bd1087d39198ef1f5f16414a4`. Branch da PR #73: `audit/ce-supabase-migration-first-20261115`. Supabase físico único `pgsybzggewhinaniybiy`. Não executar SQL mutável nem publicar candidato.

## Novas verificações
CI do commit `01c7055c4f6b853bd1087d39198ef1f5f16414a4`: Pipeline Determinístico run 44491369324 PASS; CE Migration-first Supabase provenance run 44491369314 PASS; CI - Validação run 44491369305 PASS; Canonical repository invariants run 44491369315 FAIL. 3/4 workflows PASS, global FAIL. Não atribuir a falha a causas específicas sem logs atuais. CI deste novo checkpoint NOT_RUN.

Comparações `main...branch`: `feat/ce-tools-governed-backend-20261115` 15 ahead/0 behind, 33 arquivos; `feat/cko-catalog-metamodel-automated-20261114` 22/0, 48 arquivos; `feat/cko-m08-m09-corpus-atomic-20261114` 8/0, 8 arquivos; `integration/cko-parsers-catalog-20261114` 163/0, 175 arquivos. Estas são métricas de Git, não homologação. HEADs individuais não capturados nesta rodada.

Consulta SELECT ao catálogo físico `pg_constraint` agrupada por schema/tipo:
- `ce_platform`: CHECK 3, FK 135, PK 96, UNIQUE 18 = 252.
- `cko_governance`: CHECK 61, FK 81, PK 88, UNIQUE 34 = 264.
- `public`: CHECK 53, FK 71, PK 48, UNIQUE 25 = 197.
- Total três schemas: 713. Contagens estáveis em relação ao checkpoint anterior, sem inferência de equivalência ao export.

Export histórico informado: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies. O checkpoint anterior registrou MANIFEST blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14` e constraints.jsonl blob `83642780302397204b39796e1bd3604a77c68f53`; **não revalidados** nesta rodada, pois a tentativa de ler `manifest.json` em minúsculas retornou NOT_FOUND; verificar `MANIFEST.json` com grafia exata. Export NON_ATOMIC_ACROSS_QUERIES / HOLD_HUMAN conforme checkpoint anterior.

## Programa de trabalho — objetos, fingerprints, riscos, aceite
| WO / objeto | Referência e delta | Status e teste | Risco | Responsável / próxima ação | Aceite |
|---|---|---|---|---|---|
| CI PR73 | commit 01c7055c; runs 44491369324, 44491369314, 44491369305, 44491369315 | 3/4 PASS, global FAIL | alto | Engenharia: ler logs atuais, corrigir código e testar | 4/4 PASS + smoke |
| Export MANIFEST | blob histórico 8099e3ff; delta NOT_VERIFIED | HOLD_VERIFY | alto | Dados: reler caminho exato, comparar SHA | identidade de snapshot e escopo |
| Constraints JSONL | blob histórico 83642780; 8 amostras previamente validadas sem novo delta demonstrado | 8/1996 PASS_SEMANTIC_SAMPLE históricos; 1988 não comparadas | alto | Dados: crosswalk incremental por chave e fingerprint | 1996/1996 classificadas e divergências justificadas |
| Catálogo ce_platform | SELECT 3+135+96+18=252 | PASS_READ | médio | Dados: mapear por objeto | PK/FK e definições comparadas |
| Catálogo cko_governance | SELECT 61+81+88+34=264 | PASS_READ | médio | Dados: mapear por objeto | PK/FK e definições comparadas |
| Catálogo public | SELECT 53+71+48+25=197 | PASS_READ | médio | Dados: mapear por objeto | PK/FK e definições comparadas |
| 24 ferramentas | branch ahead 15, files 33 | 0/24 NOT_RUN | alto | Engenharia/clínica: revisar contratos, RLS e testes | 24/24 gates |
| Metamodelo | branch ahead 22, files 48 | HOLD_VERIFY | alto | Arquitetura: dicionário, chaves e semântica | equivalência comprovada |
| Corpus M08/M09 | branch ahead 8, files 8 | HOLD_VERIFY | alto | Curadoria: proveniência, licenças, dedup | átomos rastreáveis |
| Parsers | branch ahead 163, files 175; 16 falhas históricas | 0/16 corrigidos nesta rodada | alto | Engenharia: confrontar arquivos e corrigir com testes | 16/16 PASS |
| Imports | 5 falhas históricas | 0/5 corrigidos nesta rodada | alto | Engenharia: testes de CLI e namespaces | 5/5 PASS |
| contracts/fonts | legado histórico | HOLD_VERIFY | alto | Engenharia: mapear consumidores antes de excluir | consumidores migrados e smoke PASS |
| Workspace PR71 | HEAD histórico 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d | NOT_RECHECKED | alto | Engenharia: preview, auth e release gates | build/auth PASS |

## Métricas, decisão e ações
CI 3/4 PASS (75% dos workflows, global FAIL); branches comparadas 4/4; crosswalk histórico 8/1996 (0,40% de cobertura de amostra, não homologação); ferramentas 0/24 revalidadas; parsers 0/16 corrigidos; imports 0/5 corrigidos. Estimativa global de conclusão **NÃO AFERÍVEL** por falta de denominadores de aceite clínico, jurídico e funcional. Testes locais novos NOT_RUN; CI pós-checkpoint NOT_RUN. Alteração funcional nesta rodada: nenhuma. Próximas ações: inspecionar logs atuais e correções reaproveitáveis da branch de parsers; conferir SHA do MANIFEST com grafia exata; ampliar crosswalk somente por delta; validar PR71. Sem DDL/DML, migrations, seeds, merge, deploy, exclusão, publicação. Fail-closed e gates clínicos, LGPD, jurídicos, segurança, licenças e proveniência mantidos. Fontes oficiais externas novas: nenhuma.
