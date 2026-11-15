# WO-20261115-2057 — Caracterização executável do guard de promoção

Escopo: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`, somente SELECT; branch `audit/ce-supabase-migration-first-20261115`; PR #73. Não envolve Neon, SOT ou contabilidade.

## Fonte física e fingerprint
- `SELECT pg_get_functiondef(...)` em `cko_governance.guard_pilot_baseline_promotion()`, consultado 2026-11-15.
- Predicado atual: `upper(new.status) ~ '(ACTIVE|ASSURED|APPROVED|PROMOTED|RELEASED|READY_FOR_RELEASE|CURRENT)'`; expressão sem âncoras.
- `SELECT status,count(*) FROM cko_governance.controlled_artifacts GROUP BY status`: 30 status distintos, 530 registros. Dados apenas para caracterização; não constituem homologação.
- Último checkpoint de base: `237def951f8fd9da390e9cd57c02104584984cc8`; commit do teste: `a3c93a2cef37c469b4b8cd93805f33ec7c2e1648`.

## Entrega de engenharia
Criado `tests/test_cko_promotion_status_predicate.py` com quatro testes de caracterização: 30 status físicos, três falsos positivos reais, seis casos adversariais e comparação com candidato de correspondência exata. Uma versão equivalente foi executada localmente via `python -m unittest discover`: **4 PASS / 0 FAIL**. O teste commitado ainda requer execução no CI do repositório; **CI NOT_RUN** nesta rodada.

**Achado de segurança semântica:** `ACTIVE_INTERNAL`, `ACTIVE_VERIFIED`, `APPROVED_NOT_DEPLOY_VERIFIED`, `NOT_APPROVED`, `UNRELEASED` e `INACTIVE` satisfazem o predicado atual por substring. Isto pode ativar o guard para estados não equivalentes a publicação; não comprova bypass nem autorização de release. O classificador exato é apenas candidato, pois status clínicos autorizados ainda não foram homologados.

## Gates e próximas ações
- PASS_CATALOG: 30/30 estados físicos observados; 530 linhas.
- PASS_OFFLINE: 4/4 testes equivalentes executados localmente.
- HOLD_SEMANTIC: matriz normativa de estados e distinção candidato/publicado não aprovada.
- HOLD_SECURITY: caminhos de escrita indiretos, privilégio de papéis e impacto do guard.
- HOLD_HUMAN: nenhuma alteração de função SQL, migration, seed, merge ou publicação.
- Próxima ação: executar teste commitado no CI, validar política canônica de estados, conferir 24 ferramentas com tabelas reais e definir diff/rollback antes de propor correção.

## Registro incremental
| Objeto | Fingerprint | Último commit | Estado | Próxima ação |
|---|---|---|---|---|
| `cko_governance.guard_pilot_baseline_promotion()` | regex não ancorada; SECURITY DEFINER; SELECT físico 2026-11-15 | `a3c93a2` | PASS_CHARACTERIZATION / HOLD_SEMANTIC | matriz de estados |
| `cko_governance.controlled_artifacts.status` | 30 valores distintos; 530 linhas | `237def951` | PASS_CATALOG | acompanhar delta físico |
| `tests/test_cko_promotion_status_predicate.py` | 4 testes; 30 reais + 6 adversariais | `a3c93a2` | PASS_OFFLINE / CI_NOT_RUN | CI |
