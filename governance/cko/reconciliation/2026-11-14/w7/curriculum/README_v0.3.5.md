# W7 v0.3.5 — fontes curriculares externas adicionais (somente metadados)

**Estado: HOLD_SYLLABUS / HOLD_EXACT_EDITION / HOLD_RIGHTS / HOLD_SEMANTIC_REVIEW / NO_GO.**

Complemento rastreável à v0.3.4: **12/12 pares preservados; 0 novas relações aprovadas; 0 publicações; 0 alterações em átomos, currículos originais, main ou Supabase.**

## Descoberta

- **PUC Minas:** ementário institucional histórico (arquivo identificado como 2024, gerado 17/11/2023; oferta 3, turma 1, modalidade assíncrona) descreve a disciplina Doenças Relacionadas ao Trabalho; não demonstra que os 3 pares W7 correspondam à edição atual com aulas ao vivo, nem que seus microtópicos específicos estejam presentes. Páginas 1–2 do PDF inspecionadas visualmente.
- **A.C.Camargo / Ibmec:** caderno do MBA Gestão em Saúde com Ênfase em Ambientes Complexos, edição 2026.1, relaciona planejamento estratégico e sustentabilidade da saúde no Módulo I, Tema 2. **Não comprova** que `CURITEM-00967` e `CORE-STRATEGIC-PLANNING` correspondam àquela edição, nem o escopo do microtópico `MICRO-WORK-00654`. Inspeção visual dos bytes originais não realizada: URL retornou 403 ao tentar a captura; hash do PDF permanece nulo.
- **Conflito entre publicações da própria instituição:** caderno do MBA aponta **472 h** e uma listagem institucional para MBA homônimo aponta **432 h**. Pode refletir versões/edições diferentes. Não normalizar carga horária sem documento de edição exata.

## Controle de fonte

Registro estruturado: `audit/EXTERNAL_SYLLABUS_DISCOVERY_DELTA_12_v0.3.5.json`. Contém URL, editor, edição conhecida, seção, limitações, conflito, classificação por ID e 10 verificações locais de metadados. Não incorpora texto protegido de terceiros, bytes originais nem autorização de direitos.

**Requisitos para avanço:** (1) recuperar versão curricular exata dos programas e identificadores; (2) confirmar microtópico e intervalo original com integridade verificável; (3) resolver divergência de edição e cargas horárias; (4) parecer humano sobre semântica e direitos; (5) CI de publicação. Até lá, todas as relações `PART_OF` seguem bloqueadas.

Fontes:
- PUC Minas: https://www.pucminas.br/PucVirtual/Pos-Graduacao/Documents/enfermagemdotrabalho2024.pdf
- A.C.Camargo / Ibmec, caderno: https://ensino.accamargo.org.br/Custom/Content/Themes/Shared/E-Book/P%C3%B3s-Gradua%C3%A7%C3%B5es%202026.1/Caderno%20MBA%20Gest%C3%A3o%20V7.pdf
- A.C.Camargo, catálogo: https://ensino.accamargo.org.br/cursos-e-programas?pg=7
