# Próxima fila de universidades de referência — W7 v0.5.5

Após USP, Einstein e Sírio-Libanês, o levantamento curricular do CKO ampliou a descoberta para **Unifesp, Unicamp, UFMG, UFCSPA, UFRJ e UFRGS**. São **nove registros**, sendo oito fontes institucionais identificadas e uma instituição aguardando recuperação da matriz primária. Nenhuma fonte de graduação é contada como curso de especialização Cofen.

## Resumo da evidência

| Universidade | Situação | Nível de granularidade |
|---|---|---|
| Unifesp — Escola Paulista de Enfermagem | Matriz **000003 ATIVA** aparece no índice da instituição; PPC/Matriz 2023 referenciados | Reabertura da matriz ativa retorna 403; conferir conteúdo de documentos vinculados |
| Unicamp — FEnf | Catálogo 2026 vinculado; horários 2026/1 e 2026/2 abertos | Listas de disciplinas ofertadas, não currículo pleno de cada turma |
| UFMG — Escola de Enfermagem | Portal do curso e versões de planos de ensino | 4.005h/10 períodos descritos; baixar versão correta das ementas |
| UFCSPA | Matriz a partir de 2023, página atualizada em 29/10/2025 | **Dez semestres**, códigos, disciplinas, horas e distinção entre tutoria e horas computadas |
| UFRJ — EEAN | Texto oficial de estrutura curricular recuperado | Referência histórica à norma de 1994, não uma matriz comprovadamente vigente em 2026 |
| UFRGS | Instituição prioritária | **HOLD**: não foi recuperada matriz primária atual, evitar inventar disciplinas |

## Fontes registradas

1. **Universidade Federal de São Paulo** — Bacharelado em Enfermagem. [Fonte](https://cursos.siiu.unifesp.br/graduacao/curso/matriz-curricular/eyJjdXJzb19pZF9jdXJzbyI6IjUiLCJjb2QiOiIzIn0%3D/detalhes). Edição: `MATRIZ_000003_ATIVA_EM_2026`; estado: `OFFICIAL_INDEX_FULL_MATRIX_WITH_TERM_TABLES_DIRECT_WEB_FETCH_403`; extração: `DISCIPLINE_CODE_HOURS_TERM_TABLE_IN_SEARCH_INDEX`.

2. **Universidade Federal de São Paulo** — PPC e matriz curricular 2023 do Bacharelado. [Fonte](https://graduacao-epe.unifesp.br/sobre/ppc-e-matriz-curricular). Edição: `PPC_AND_MATRIX_2023_LISTED_AS_CURRENT_IN_OFFICIAL_PAGE`; estado: `OFFICIAL_PAGE_OPENED_LINKS_PRIMARY_GOOGLE_DRIVE_DOCUMENTS`; extração: `PRIMARY_DOCUMENT_LINKS_NOT_YET_RETRIEVED_FULL`.

3. **Universidade Estadual de Campinas** — Catálogo de graduação Enfermagem 2026. [Fonte](https://www.fenf.unicamp.br/graduacao/vida-academica/disciplinas/). Edição: `CATALOGO_2026_LINKED`; estado: `OFFICIAL_PAGE_OPENED_CATALOG_2026_LINK`; extração: `CATALOG_REDIRECT_MUST_RESOLVE_CURRICULO_PLENO_BY_COHORT`.

4. **Universidade Estadual de Campinas** — Caderno de horários de Enfermagem 2026/1 e 2026/2. [Fonte](https://www.dac.unicamp.br/portal/caderno-de-horarios/2026/1/S/G/FENF). Edição: `2026_1_AND_2026_2`; estado: `OFFICIAL_PAGE_OPENED_TWO_SCHEDULES`; extração: `LISTED_CODE_AND_DISCIPLINE_PER_SEMESTER`.

5. **Universidade Federal de Minas Gerais** — Bacharelado em Enfermagem — estrutura e percursos. [Fonte](https://www.enf.ufmg.br/?page_id=8239). Edição: `ACTIVE_COHORT_VERSION_NOT_IDENTIFIED`; estado: `OFFICIAL_COURSE_PAGE_OPENED`; extração: `COURSE_SCOPE_HOURS_PROGRESS_AND_PREREQUISITE_CONTEXT`.

6. **Universidade Federal de Minas Gerais** — Versões curriculares e planos de ensino. [Fonte](https://www.enf.ufmg.br/?page_id=2379). Edição: `VERSIONS_BY_INSTITUTIONAL_CURRICULUM_UNCONFIRMED`; estado: `OFFICIAL_PAGE_OPENED_GUIDES_TO_VERSIONED_TEACHING_PLANS`; extração: `PLAN_BY_CURRICULAR_VERSION_LINKED_DOWNLOAD_PENDING`.

7. **Universidade Federal de Ciências da Saúde de Porto Alegre** — Bacharelado em Enfermagem — matriz a partir de 2023. [Fonte](https://ufcspa.edu.br/vida-academica/graduacao/cursos/enfermagem/matriz-curricular). Edição: `MATRIX_FROM_2023_PAGE_UPDATED_2025-10-29`; estado: `OFFICIAL_PAGE_OPENED_FULL_TABLE`; extração: `FULL_10_SEMESTER_GRADE_WITH_CODES_CLOCK_HOURS_AND_TUTORIAL_FLAGS`.

8. **Universidade Federal do Rio de Janeiro** — Estrutura Curricular — texto legado. [Fonte](https://www.eean.ufrj.br/index.php/grupos-de-pesquisa/17-graduacao/87-estrutura-curricular). Edição: `HISTORIC_1994_REFERENCES_NOT_PROVEN_CURRENT_2026`; estado: `OFFICIAL_PAGE_OPENED_HISTORICAL_PROGRAM_NARRATIVE`; extração: `HISTORIC_CYCLES_AND_CREDIT_HOURS_NOT_CURRENT_MATRIX`.

9. **Universidade Federal do Rio Grande do Sul** — Bacharelado Enfermagem — matriz a recuperar. [Fonte](https://www.ufrgs.br/eenf). Edição: `UNKNOWN`; estado: `PRIMARY_CURRICULUM_NOT_RETRIEVED_DIRECT_SITE_OPEN_TIMED_OUT`; extração: `NO_COURSE_GRADE_VERIFIED`.

## Pontos técnicos que afetam a atomização

- Não equiparar ofertas de um único semestre a grade curricular vigente de todas as turmas.
- Não converter matriz da graduação em reconhecimento profissional de uma especialidade.
- Na UFCSPA, conferir **conflito de código ENF04004** e repetição de `XENF01001` antes de deduplicar componentes; controlar estágio, optativas e tutoria em métricas separadas.
- Manter graduação, residência, especialização e cursos multiprofissionais em camadas diferentes. A base comum apoia o currículo básico, mas não prova o conteúdo avançado de todas as especialidades.
- Contar programa institucional uma vez por identidade/edição e manter múltiplas fontes como evidências, sem replicar programas.
- A fonte pública não autoriza a cópia do texto integral de ementas, slides ou livros. É permitido mapear metadados e redigir conteúdo autoral com fundamento próprio, observada a legislação aplicável.

## Próximas etapas

1. Completar a extração de títulos/códigos/horas da matriz UFCSPA; verificar conflitos de identidade.
2. Recuperar os PDFs PPC e Matriz 2023 Unifesp e a matriz 000003 ativa por canal institucional autorizado.
3. Resolver o currículo pleno 2026 da Unicamp por turma e ementas da UFMG por versão.
4. Localizar a matriz vigente UFRJ e UFRGS sem usar fonte histórica como atual.
5. Voltar ao eixo de especializações COFEN e buscar universidades/hospitais de referência por especialidade, não confundir qualidade da graduação com currículo de pós.
6. Atomizar afirmações científicas separadamente; deduplicar por claim/versionamento, preservar direitos e gates clínicos.

**Status:** fontes catalogadas; curricularização e direitos não homologados; `NO_GO_PUBLICATION`. GitHub W7 de revisão, sem merge/deploy e sem escrita no Supabase.
