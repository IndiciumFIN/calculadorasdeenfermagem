# CE / CKO / NCOS — migration-first: Supabase canônico (15/11/2026)

**Status: READ_ONLY / HOLD_HUMAN.** Nenhuma migration executada, nenhuma alteração de tabela, RLS, histórico ou publicação. Neon NÃO foi adotado como banco. Os detalhes auditáveis estão em `docs/migration-crosswalk-supabase-ce-20261115.json`.

## Procedimento e fontes verificadas

- Banco: Supabase **Calculadoras-Smart** `pgsybzggewhinaniybiy` (PostgreSQL 17). Fontes: `supabase_migrations.schema_migrations`, `information_schema.columns`, `pg_class`, `pg_constraint`, `pg_index`, `pg_policies`, privilégios `anon/authenticated` e contagens `SELECT count(*)`, tudo em **somente leitura**.
- Código: `IndiciumFIN/calculadorasdeenfermagem@main`, duas fontes `supabase/migrations/` conferidas bit a bit por SHA-256 e SHA de blob Git, conforme o manifesto.
- Técnica oficial: https://supabase.com/docs/guides/deployment/database-migrations e https://supabase.com/docs/guides/api/securing-your-api.
- **255 migrations remotas, 255 versões únicas**. Nem `20261011000000` nem `20261011120000` aparece no histórico. Nenhuma das quatro tabelas legadas existe fisicamente em `public`. Isso NÃO prova necessidade de executá-las.

## Crosswalk com chaves, segurança e semântica

| SQL legada | Objeto(s) do banco já existente(s) | Situação e delta ainda não comprovado |
|---|---|---|
| `public.normatives` (`id_canonico`, `titulo`, `tipo`, `numero`, `ano`, `orgao`, `status`, `link_fonte`) | `cko_governance.normative_reference_catalog` (362 registros, PK `normative_ref`), `cko_evidence.sources` (157, PK `source_id`) | Não equivalentes por declaração; crosswalk de identidade, fonte oficial, versão temporal, direito de uso, vigência, tipo e número |
| `public.atoms` (`normative_id` FK, `texto_regra`, `dispositivo_legal`) | `xlf_publication.content_atom` (108, FK `publication_id`), `xlf_reg.evidence_atomic` (66, FK `source_id` e `command_id`), `calculadoras_de_enfermagem.document_atomization` (ledger de processo) | Três domínios DIFERENTES. Não existe prova de uma relação normativa→artigo→regra→átomo clínico; não migrar texto automaticamente |
| `public.calculators` (`slug`, `parametros`, `atom_ids`) | `ce_platform.canonical_objects` (320) → `ce_platform.clinical_tools` (111), FK `canonical_id` de um para um. `clinical_evidence_bindings` existe com FK para `clinical_tools`, mas **0 linhas** | Reutilizar núcleo canônico; o **delta prioritário é vincular evidências verificadas**, não criar outra `calculators`; autorização clínica `HOLD_HUMAN` |
| `public.registry` (`hash_sha256`, `drive_file_id`, `find_ids`) | `ce_platform.source_mappings` (215, FK para `canonical_objects`), `external_registry_bindings` (8, unicidade composta), `xlf_reg.registry_item` (24, sem equivalência semântica automática) | Determinar hash, origem, revisão, chaves de fonte, FIND e rastreabilidade por campo |

## Risco P0: leitura pública indiscriminada nas duas fontes antigas

Os quatro objetos legados trazem política `FOR SELECT USING (true)` após `ENABLE ROW LEVEL SECURITY`. **Isso não impede acesso a rascunhos, fontes não homologadas, direitos pendentes ou normas em análise.** Não aplicar em `public`, nem copiar políticas. Os objetos canônicos amostrados têm `anon_select=false` e `authenticated_select=false` e os schemas não concedem `USAGE` para esses papéis. `cko_governance.normative_reference_catalog` e `cko_evidence.sources` não possuem RLS, mas também não estão acessíveis aos papéis citados. Não extrapolar para todos os schemas nem confundir restrição atual com autorização clínica.

## Diferenciação obrigatória das migrations

O conjunto de **96 SQL raiz** nos cinco repositórios do Workspace/espelhos utiliza mecanismo próprio (`_migrations` ou PGlite); **não** é a lista de migrations `supabase_migrations.schema_migrations`. Não copiar essas SQLs para o Supabase. As **duas SQLs locais** deste repositório estão **HOLD_SEMANTIC_CROSSWALK**; 255 versões remotas ficam intactas. `APPROVED_MIGRATIONS=0`; número do delta físico incremental continua **UNKNOWN**.


## Verificação adicional das relações existentes (15/11/2026)

A tabela `ce_platform.source_mappings` contém **215 vínculos, todos `CANDIDATE_HOLD`**. Em `ce_platform.canonical_objects`, **todas as 111 ferramentas associadas a `clinical_tools` permanecem com `publication_state` em `HOLD` ou `HOLD_HUMAN`**. A tabela específica `ce_platform.clinical_evidence_bindings` tem **0 linhas**. Esse achado NÃO autoriza afirmar que não existam vínculos evidenciais em outros schemas; evidencia que a relação canônica central ainda não foi operacionalizada para esse conjunto.

O catálogo `cko_evidence.sources` contém **157 registros**, incluindo origens `ACCREDITED`, `CONTROLLED_DISCOVERY` e `PENDING_BOARD_REVIEW`. A existência de uma fonte acreditada não promove uma ferramenta automaticamente: cada vínculo precisa corresponder a dispositivo, versão, direito de uso, regra e responsável pela validação. **O P0 real é qualidade da relação, não criação de tabela legada.**

## Gates de liberação

1. Completar crosswalk de identidade e versionamento (PK, FK, índice, tipo, RLS, grants, direitos, normativo oficial, trecho/âncora, evidência, status editorial e clínico).
2. Priorizar os **0 vínculos clínicos** existentes na tabela `clinical_evidence_bindings`: recuperar fonte validada, validar regra e ligação clínica, evitar seed inventado ou PASS falso. Qualquer alteração em produção depende de WO.
3. Propor apenas delta incremental demonstrado em tabela canônica, com versões imutáveis, testes de reexecução, rollback/restore, revisão de segurança, jurídico e clínica.
4. Somente então submeter `HOLD_HUMAN` para decisão de execução. Não executar SQL, `db push`, `migration repair`, `db reset` ou merge com efeito no banco com base neste relatório.

## Controle automatizado de origem (não é um migrador)

`python scripts/check_supabase_migration_guard.py --report` confere os arquivos existentes contra SHA-256, detecta alterações, arquivo inesperado e tentativas de promoção no manifesto, **sem conexão remota**. Retorna 2 (HOLD) deliberadamente. `python -m unittest discover -s tests -p 'test_supabase_migration_guard.py'` testa o contrato. Esse guard não prova equivalência semântica e não bloqueia ferramentas externas de aplicação por si só; só vira exigência operativa quando vinculado aos Rulesets/CI relevantes.
