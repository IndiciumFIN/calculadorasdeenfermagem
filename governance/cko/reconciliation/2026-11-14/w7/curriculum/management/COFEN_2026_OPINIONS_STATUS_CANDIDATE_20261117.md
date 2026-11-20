# CKO W7 — pareceres oficiais Cofen 2026: relações semânticas e estado normativo (candidato)

**Consulta:** 2026-11-17. **Status:** CANDIDATE / HOLD_SOURCE_VERSION / HOLD_HUMAN. **Escopo:** reconciliação de evidência normativa, sem atualizar catálogo ou direitos de reprodução.

## Âncora normativa e proposta

- Resolução Cofen 581/2018, página oficial com alterações 610/2019, 625/2020 e decisões 065/2021, 120/2021, 263/2023, 264/2023 e 21/2024: https://www.cofen.gov.br/resolucao-cofen-no-581-2018/
- Comunicado de 25/09/2026: GT **concluiu proposta** de revisão e entregou relatório; não é ato normativo promulgado: https://cofen.gov.br/gt-conclui-proposta-de-revisao-sobre-registro-das-especialidades-de-profissionais-da-enfermagem/
- A busca pública desta rodada não forneceu ato substitutivo promulgado e comprovado. **Ausência de resultado não prova inexistência.** Manter `HOLD_ENACTMENT` e não substituir a lista vigente.

## Três pareceres distintos, não deduplicar por referência à Resolução 581

| Identidade documental | Evidência oficial | Relação candidata | Decisão permitida |
|---|---|---|---|
| Parecer 15/2026, CT Enfermagem; aprovado em plenário em 30/01/2026 segundo o texto | https://www.cofen.gov.br/parecer-no-15-2026-camaras-tecnicas-de-enfermagem/ | `INTERPRETS` 581/2018 + 625/2020; curso 'Licitações e Contratos Administrativos' não enquadrado como especialidade | **Não** criar especialidade nem importar conteúdo de contabilidade/administração para CE |
| Parecer 25/2026, CT Enfermagem | https://www.cofen.gov.br/parecer-no-25-2026-camaras-tecnicas-de-enfermagem/ | `RECOMMENDS_TO_PLENARY` registro de formação pedagógica complementar; distingue expressamente curso de especialidade Educação em Enfermagem | **Não** afirmar registro concedido sem decisão plenária final individualizada |
| Parecer 16/2026, CT Enfermagem, publicado em 30/03/2026 | https://www.cofen.gov.br/parecer-n-16-2026-camaras-tecnicas-de-emfermagem/ | `RECOMMENDS_TO_PLENARY` registro de título de residência em Cardiologia; especialidade já listada no anexo (Área I, item 7) | **Não** criar nova especialidade ou generalizar deferimento a todas as edições/coortes |

## Regras de conciliação sem duplicação

- Chave primária de fonte: `cofen:parecer:<numero>:2026:<camara>`; manter URL, data observada, data do ato e eventual decisão plenária como campos separados. Não mesclar pareceres 15, 16 e 25, mesmo quando citam a mesma norma.
- Chave normativa: `cofen:resolucao:581:2018` + arestas `AMENDED_BY` por ato individual; a notícia de GT recebe tipo `PROPOSAL_NOTICE`, nunca `AMENDS`.
- Chave acadêmica: instituição + curso + edição/coorte + campus + documento ementa. Parecer de caso individual não comprova matriz curricular de edição diversa.
- Direitos: URL pública comprova acessibilidade, **não** licença de cópia integral, redistribuição ou treinamento. Registrar `HOLD_RIGHTS` para cada operação não autorizada.
- Regras de promoção: somente após verificar íntegra da norma, publicação/eficácia, versões, decisões plenárias aplicáveis e revisão jurídica/curricular humana. Não derivar conteúdos clínicos de pareceres sobre registro profissional.

## Checklist de testes candidatos (não executados)

1. Notícia `PROPOSAL_NOTICE` nunca promove `norm_status=IN_FORCE`.
2. Parecer `RECOMMENDS_TO_PLENARY` nunca equivale a `FINAL_REGISTRATION_GRANTED`.
3. Curso complementar não cria automaticamente `SPECIALTY`.
4. Citação repetida da 581 em pareceres distintos não deduplica as identidades documentais.
5. Nenhum link público concede automaticamente `COPY_REUSE_LICENSE=YES`.

**Bloqueios:** HOLD_ENACTMENT, HOLD_SOURCE_VERSION, HOLD_HUMAN, HOLD_RIGHTS; sem impacto no CI canônico existente. Denominadores históricos mantidos, não recalculados: 65/65 especialidades catalogadas, 14/65 com anúncios na amostra, 38/1055 microaulas candidatas, 0/22 bloqueios canônicos corrigidos.
