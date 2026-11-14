# W7 v0.2.7 — auditoria de todas as branches e Supabase antes da integração

**HOLD_MERGE / HOLD_VALIDATORS / HOLD_CANONICAL_IDS / HOLD_RIGHTS / HOLD_CLINICAL / NO_GO**

## Fatos observados
- Inventário de 128 branches: 70 de calculadorasdeenfermagem, 57 de dev-chatgpt-workspace e 1 em repositório privado (somente agregado publicado). Duas duplas de branches dos repositórios públicos compartilham HEAD SHA.
- Comparação de 37 branches públicas de maior relevância contra suas mains e seis comparações cruzadas entre candidatas. Os demais ramos foram inventariados por nome/SHA; não se afirma revisão de conteúdo integral.
- PR #61 empilhada sobre #60: branch de parsers/catalog com 159 commits e 171 caminhos à frente da main; evitar mesclar as PRs de parsers e metamodelo separadamente sem reconciliação de arquivos.
- O compilador de catálogo/dicionário canônico já existe em scripts/cko_catalog.py e não deve ser refeito em implementação concorrente.
- Os nove validadores do HEAD atual de integration/cko-parsers-catalog retornam False e HOLD. O relatório antigo que afirma return True refere-se a código anterior; estado atual é seguro para negação, mas inválido como validador funcional.
- Relatório de integração atual indica 11/16 parsers e cinco pendentes: atlas, cdsi, esavi, sinan, taco. Contagem baseada no relatório de integração; execução runtime não repetida nesta auditoria.
- Supabase somente leitura: 157 sources, 41 claims, 103 fragments, 84 snapshots, 22 evidence bundles, 7558 relation rows (6930 controlled candidates), 320 canonical objects em HOLD/BLOCKED, 215 source mappings e 38 platform relations sem pontas órfãs no join.
- Zero registros em ce_platform.content_documents, content_blocks, courses, questions, assessments e clinical_evidence_bindings. Isso não significa falta de conteúdo nos arquivos Git ou Drive.
- Os 46 IDs de claims PMO M08/M09 do blob 0275f657edd5b2e4ec4cd66cb99b760fa2807019 foram comparados em SQL e 0 coincidem por ID com os 41 claims do banco. Sem concluir ausência semântica ou autorizar importação.
- 89 registros no agent_registry; catálogo de agentes não é prova de execução operacional.
- RLS desligado em 7/7 tabelas de cko_evidence e 6/6 cko_master, porém nenhum USAGE para anon/auth nesses schemas foi observado. NÃO afirmar vazamento; auditar efetiva exposição API e grants.

## Sequência proposta antes de integração
1. Usar a W7 como livro de achados e proveniência; manter as branches originais e a main intactas.
2. Reusar PR61 como candidata técnica, em conjunto com a base PR60 e o catálogo de metamodelo existente; reconciliar blobs e contratos, nunca merge em lote.
3. Implementar human_review_validator e schema_validator com provas positivas/negativas e credenciais autorizadas; depois os outros sete e os cinco parsers faltantes, sem falsos PASS.
4. Resolver a correspondência por identidade e semântica dos 46 claims e o ledger de direitos antes de qualquer inserção na projeção da plataforma.
5. Preservar 17 JSONLs de PDFs em HOLD de durabilidade e UC08 em HOLD curricular; não inventar módulos/fragmentos.
6. Executar CI estrito ligado ao HEAD, testes de segurança, revisão humana independente; somente depois PR de integração deliberada.

## Escopo e privacidade
Os arquivos desta versão incluem somente metadados dos dois repositórios públicos. O repositório privado é contado, mas seus nomes de branches, hashes, conteúdo e caminhos NÃO são republicados. A auditoria não modifica Supabase, Drive, outras branches, main, deploy nem realiza revisão clínica.

**Todos os achados históricos da W7 v0.2.0 a v0.2.6 permanecem preservados.**
