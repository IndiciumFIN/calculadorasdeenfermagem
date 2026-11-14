# CKO — W7 / Reconciliação dos acervos curriculares, fontes e átomos

**CANDIDATE / PROVENANCE_INTEGRITY_PASS / HOLD_CURRICULUM / HOLD_RIGHTS / HOLD_CLINICAL / NO_GO**

## Resultado conferido
- 46/46 afirmações M08/M09 verificadas por IDs exatos fonte→documento→átomo, localizador e SHA-256 do texto e documento. Nada foi homologado.
- Corpus Drive: 118 fontes, 124 documentos, 28.001 átomos, 9.102 vínculos candidatos, 114 programas, 985 itens, 182 tópicos normalizados e 1.514 vínculos curriculares.
- Seleção por IDs de especialidade: 17 programas, 162 itens curriculares únicos, 274 mapeamentos de tópicos e 30 relações CONTEXT_ONLY de programa→W4/W5/W6.
- W5: 8/8 átomos normativos ainda sem hash primário do trecho. W6: 6/6 fontes sem hash do fragmento.
- O catálogo curricular institucional não se confunde com a grade autoral de Cardiologia (10 UCs/51 módulos/295 tópicos, UC08 em conflito), nem autoriza carga horária para CME/SRPA.

## Arquivos desta reconciliação
- `evidence/46_claim_atom_exact_hash_checks.jsonl`: verificações de proveniência, sem texto original protegido.
- `curriculum/162_curriculum_items_four_contexts_candidate.jsonl`: vínculos estruturais do currículo transversal; os títulos são metadados e não conteúdo clínico.
- `curriculum/program_to_w4_w5_w6_context_only.jsonl`: relações com os recursos W4.1/W5/W6; estritamente contexto curricular.
- `sources/w5_w6_source_identity_candidate_crosswalk.jsonl`: correspondências de fontes entre waves e corpus (não autorizadas automaticamente).
- `evidence/w5_norm_atoms_hash_gaps.jsonl`: lacunas normativas abertas.
- `qa/RECONCILIATION_QA.json`: resumo, testes e gates.

## Localização dos originais (não incluídos)
- Drive: https://drive.google.com/drive/folders/1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC
- M08/M09: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/39
- W4.1: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/66
- W5 CME: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/67
- W6 Centro Cirúrgico / SRPA: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/68

## Guardrails
- Correspondência de IDs e de hashes NÃO comprova suporte semântico da afirmação, vigência da norma, direitos ou aptidão clínica.
- Reconciliação institucional apenas cria candidatos. Não transformar `DISCIPLINE` institucional em `MODULE` do produto sem chancela.
- Não agrupar CME com Centro Cirúrgico, não transformar Cardiologia em módulo, não promover claims ou normas automaticamente.
- Não modificar main/Supabase e não liberar conteúdo publicado sem evidência, direitos, revisão humana e validação clínica.
