# W7 v0.3.0 — 30 novos títulos curriculares recuperados de cronogramas institucionais

**ESCOPO EXCLUSIVO: conteúdos curriculares atomizados como títulos de disciplinas, não claims clínicos.**

Foram localizados três cronogramas 2026/2027 de Enfermagem do Ensino Einstein, em URLs controladas pelo provedor. Eles correspondem precisamente aos IDs que estavam na fila de 28 programas em escopo sem currículos detalhados:
- `PG-EIN-UE-EAD`, EAD Emergência e Urgência: 10 títulos, cronograma 2026-4BM.
- `PG-EIN-ICU-EAD`, EAD Terapia Intensiva: 10 títulos, cronograma 2026-5BM.
- `PG-EIN-PEDNEO-ICU`, Terapia Intensiva Pediátrica e Neonatal: 10 títulos, cronograma 2026-1BM.

A extração preserva título e link institucional no registro, sem republicar PDFs. Os dois primeiros PDFs tiveram texto e imagem visual examinados; a terceira fonte teve seu texto estruturado inspecionado, mas a captura visual falhou por cache da ferramenta. Não se calculou hash de PDF porque os bytes originais não foram recuperados localmente. Portanto, são **candidatos à admissão**, não provas finais de custódia.

Os 985 átomos anteriores permanecem imutáveis. Esta versão adiciona **30 átomos novos separados**, e não altera o status persistido dos 31 programas da v0.2.9. Os 25 outros programas em escopo não foram declarados inexistentes: apenas não receberam nova evidência granular nesta rodada.

Atividades obrigatórias, Opening Day, estágio e datas de videoconferências foram excluídos da lista de disciplinas; cargas horárias e ementas completas não foram inferidas. Uma mesma disciplina chamada Prática Baseada em Evidências ocorre em três programas, com três identidades preservadas. O exame local de nomes normalizados não encontrou coincidência exata com os 985 títulos antigos.

**Gates:** HOLD_SOURCE_BINARY / HOLD_RIGHTS / HOLD_SEMANTIC_REVIEW / NO_GO. Não houve merge, publicação, atualização do Supabase nem geração editorial.

Arquivos:
- `CURRICULAR_DISCIPLINE_ATOMS_30_v0.3.0.jsonl`
- `CURRICULAR_PRIMARY_DISCOVERY_SOURCES_3_v0.3.0.json`
- `PROGRAM_COVERAGE_DELTA_3_v0.3.0.jsonl`
- `CROSS_PROGRAM_REPEATED_DISCIPLINE_TITLES_v0.3.0.jsonl`
- `SOURCE_DISCOVERY_SUMMARY_v0.3.0.json`
- `QA_CURRICULUM_DISCOVERY_v0.3.0.json`
- `README_v0.3.0.md`
