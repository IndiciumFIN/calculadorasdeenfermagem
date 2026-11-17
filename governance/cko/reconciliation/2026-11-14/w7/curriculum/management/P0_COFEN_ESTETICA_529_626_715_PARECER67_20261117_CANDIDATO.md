# P0 — Reconciliação por edição: Enfermagem Estética (candidato, 17/11/2026)

**EPIC:** #74 · **PR:** #70 · **WO:** 01 (versões), 02 (direitos), 04 (currículo) · **Estado:** CANDIDATE / NO-GO · **Fonte:** portais oficiais Cofen consultados em 17/11/2026. Não altera catálogo, habilitações, claims clínicos ou produção.

## Evidências primárias e identidade documental

| ID do ato | Tipo / data da página | Localizador oficial | Efeito documental verificável |
|---|---|---|---|
| COFEN-RES-529-2016 | Resolução, 09/11/2016; texto consolidado no portal | https://www.cofen.gov.br/resolucao-cofen-no-05292016/ | Norma-base da atuação em estética; página marca dispositivos anteriores substituídos |
| COFEN-RES-626-2020 | Resolução, página de 21/02/2020 | https://www.cofen.gov.br/resolucao-cofen-no-626-2020/ | Altera art. 1º da 529/2016 e revoga seu anexo (arts. 1º–2º) |
| COFEN-RES-715-2023 | Resolução de 30/01/2023, página de 02/02/2023 | https://www.cofen.gov.br/resolucao-cofen-no-715-2023/ | Substitui art. 4º da 529/2016: pós-graduação lato sensu em estética e no mínimo 100 horas de aulas práticas supervisionadas |
| COFEN-PAR-67-2026 | Parecer, página de 11/11/2026, processo 00196.004464/2026-92 | https://www.cofen.gov.br/parecer-no-67-2026-camaras-tecnicas-de-enfermagem/ | Analisa proposta curricular FACUMINAS; não concede registro automático de títulos |

**Cadeia de edição:** 529/2016 —[ART_1_AMENDED_BY]→ 626/2020; 529/2016 —[ANNEX_REVOKED_BY]→ 626/2020; 529/2016 —[ART_4_AMENDED_BY]→ 715/2023. As relações são **candidatas** para validação jurídica; não criar equivalência automática entre especialidades nem afirmar que todo o conteúdo histórico do anexo permanece válido.

**Parecer 67/2026:** aprovado na 7ª Reunião Extraordinária do Plenário em 08/10/2026, segundo o próprio documento; trata de uma proposta de componente presencial supervisionado de curso FACUMINAS de 720h, e condiciona a averbação de cada egresso à prova individual de cumprimento dos requisitos. Verificação adicional possível via SEI: código 2309752, CRC 018242ED, conforme a página oficial. **Não** inferir aprovação genérica de cursos, coortes, estudantes ou modalidade EAD; a página não fornece PPC/ementa integral por edição nem históricos individuais.

## Reconciliação sem duplicação e chaves

- Chave do ato: `issuer=COFEN|type=RES/PAR|number|year`; manter edições separadas e preservar vínculo de alteração por artigo, não substituir a 529 pela 715.
- Chave de programa candidato: `provider=FACUMINAS|program=pos-lato-sensu-enfermagem-estetica|edition=UNKNOWN|campus=UNKNOWN`. **Não** computar como nova edição curricular validada ou nova especialidade.
- Fonte de currículo: parecer sobre proposta ≠ PPC/ementa oficial de edição ≠ prova de oferta vigente ≠ registro de egresso.
- Não copiar conteúdo integral dos atos, parecer ou material da IES; registrar somente metadados, localizadores e paráfrases curtas enquanto direitos por operação não forem verificados.

## Testes candidatos de regressão (NÃO executados)

1. Artigo 4º de 529/2016 consolidado referencia a redação da 715/2023, sem duplicar a redação revogada como vigente.
2. Anexo da 529/2016 não pode ser usado como catálogo vigente de procedimentos após a revogação indicada na 626/2020.
3. Um parecer favorável a componente curricular não implica `course_approved=true`, `individual_title_registered=true` ou `license_granted=true`.
4. Campo `practical_supervised_hours` não é preenchido com as 720 horas totais do curso; exigir prova própria das 100 horas mínimas e da edição.
5. Um programa sem `edition` e `campus` não é deduplicado contra outro programa por semelhança lexical, nem promove relação semântica.
6. Evidência de atuação em estética não promove automaticamente competência em Saúde da Mulher; preservar a ressalva do Parecer 37/2026.

## Bloqueios e próximos insumos

- `HOLD_SOURCE`: obter PPC, matriz e ementa **por edição/coorte/campus** da FACUMINAS e documentação de práticas; não inferir a partir do parecer.
- `HOLD_SOURCE_VERSION`: verificar publicação no DOU, eventual mudança posterior e correspondência com IDs canônicos antes de ativar regras.
- `HOLD_RIGHTS`: licença por obra, edição e operação para eventual extração/atomização, distinta de acesso público.
- `HOLD_HUMAN`: parecer jurídico, currículo e validação profissional por pessoa competente; o parecer do Cofen não substitui revisão do projeto.
- `HOLD_CI_CANONICAL`: invariantes do repositório não resolvidos; documentação não corrige parser ou import.

**Medição:** 4/4 documentos oficiais do conjunto focal consultados (100% de *triagem documental deste recorte*, não do universo de fontes); 0 novas ementas de edição validadas; 0 aprovações humanas; 0 testes executados; 0 promoções. Denominadores globais históricos preservados: 65/65 catalogadas, 14/65 com anúncios, 38/1055 rascunhos Trabalho/Urgência, 0/22 achados canônicos resolvidos. Sem percentual global artificial.
