# Auditoria de reaproveitamento P0 — PRs #63, #65 e candidata #61
**Data:** 2026-11-14. **Classificação:** `READ_ONLY_AUDIT / TECHNICAL_CANDIDATE / CLINICAL_HOLD`.  
**Repositório:** `IndiciumFIN/calculadorasdeenfermagem`.  
**Branch destino:** `integration/cko-parsers-catalog-20261114` (PR #61, base PR #60).  
**Branch main no início da rodada:** `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.

## Comparação por commit Git e prevenção de redundância
- PR #63: `f636ca88cd2f587866b4b350111b02ea6c374d78`, 15 arquivos exclusivos de um piloto COFEN/COR de ingestão offline, contratos candidatos, crosswalk, 25 testes originais e inventários de HOLD.
- PR #65: `a2b57abf244aeac42139c5f94d8cddff1575b8a6`, 22 arquivos, 20 já sobrepostos à PR #61. Verificados hashes **idênticos dos três parsers**:
  - FHIR R4: `64e0aaef0274794b04d8187d9c802e87d42317b1`;
  - MedlinePlus: `aaff2ee68199184fc6d566b02c6f0388391811af`;
  - MeSH: `14ad9871227e39a22046588b0f6ea9dea8435a42`.
- A PR #65 mantém um teste útil de integração. Foi reutilizado somente `tests/test_cko_p0_parser_integration.py` (blob `70d2ddfbcf8123d239647d32b60eb5cc3a3dfd1f` antes da adaptação), retirando a asserção obsoleta de **13** parsers faltantes. O número é calculado pelo gate canônico; o teste não deve bloquear a instalação legítima de novos módulos.
- O workflow independente da PR #65 não foi duplicado: o CI da candidata já executa FHIR, MedlinePlus e MeSH com os seus próprios testes e agora inclui o teste complementar de integração.

## Falha de confiança identificada na PR #63 e correção
O crosswalk importado registrava `verified_against_primary=true` quando o **próprio ZIP não confiável** declarava esse booleano. Isso não prova que o fragmento foi confrontado por um verificador independente com a versão oficial. Também validava `fragment_sha256` apenas pela forma hexadecimal — não ligava esses bytes à fonte oficial custodiada.

**Correção aplicada na PR #61:** o booleano recebido é apenas uma autodeclaração, jamais aprovação; foram adicionados `UNTRUSTED_PRIMARY_VERIFICATION_FLAG` e `PRIMARY_VERIFICATION_RECEIPT_MISSING`, `claims_verified_against_primary=0` enquanto não existir um verificador independente com evidência autenticada, e `primary_receipt_validation=NOT_IMPLEMENTED_HOLD`. Não foi criada implementação enganosa de assinatura/verificação nem criado recibo de humano.

Outros endurecimentos: rejeição de nomes ZIP duplicados, path traversal, symlink, membros criptografados, leitura com cota de 16 MB por registro/arquivo selecionado e até 64 MB para registros/átomos lidos. Testes adversariais acrescidos e workflow específico PR #63 preservado. O piloto segue **isolado**, sem integração operacional ao Kernel, e não autoriza `fetch` em produção.

## Origem normativa oficial e vigência
- [Resolução COFEN 429/2012](https://www.cofen.gov.br/resoluo-cofen-n-4292012/) — **revogada** pela Resolução 754/2024; preservar documentos e claims como **históricos**, não fundamentar recomendações vigentes.
- [Resolução 754/2024](https://www.cofen.gov.br/resolucao-cofen-no-754-de-16-de-maio-de-2024/) — o art. 9º declara a revogação e o art. 7º remete aos registros sob a 736/2024.
- [Resolução 736/2024](https://www.cofen.gov.br/resolucao-cofen-no-736-de-17-de-janeiro-de-2024/) — Processo de Enfermagem. Referências no preâmbulo podem citar normas que eram vigentes em janeiro/2024; não inferir vigência atual de ato citado.
- [Resolução 514/2016](https://www.cofen.gov.br/resolucao-cofen-no-05142016/) — guia de registros de enfermagem. A publicação oficial existe, mas a aplicabilidade e as referências superadas do guia exigem revisão normativa e editorial.

## Fila sem IDs fictícios
`pilots/cko-cofen-cor/evidence/PRIMARY_REVIEW_QUEUE_23.v1.json` reconcilia o inventário do piloto **por documento**, não por IDs individuais indisponíveis na branch:
| Documento | Claims reportados | Verificações oficiais de fragmento |
|---|---:|---:|
| 429/2012 (histórico) | 4 | 0 |
| 514/2016 | 2 | 0 |
| 736/2024 | 9 | 0 |
| 754/2024 | 8 | 0 |
| **Total** | **23** | **0** |

A **página oficial** localizada não equivale a SHA do **artefato oficial** nem à verificação do **fragmento usado em cada claim**. Esses artefatos/offsets/IDs de claim e recibos de revisão não foram disponibilizados no código da PR #63; permanecem **pendentes**, sem suposição de autoria, direitos ou aceite.

## Testes e limites de aceitação
- CI específico da PR #63 no commit `f636ca88`: [#43610241406](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43610241406) **PASS**.
- PR #65: [#43609826642](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43609826642) **PASS** dos três parsers.
- Novo piloto integrado: [#43611924340](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43611924340) **PASS, 28 testes**, antes dos três testes adicionais da fila (a confirmar no HEAD seguinte).
- Novo CI conjunto: [#43611919467](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43611919467), job técnico **PASS**, gate estrito **FAIL correto** (5 parsers ausentes, 9 validadores em HOLD).
- 23 claims sem verificação independente; quatro de norma revogada; 12 campos canônicos legados não resolvidos; nenhum claim promovido.
- Direitos por operação, revisão normativa/clínica independente, G6 e main merge não são supridos por PASS sintético.

**Decisão:** `TECHNICAL_CANDIDATE_PASS` somente para o subconjunto testado; `PRIMARY_PROVENANCE_HOLD`, `RIGHTS_HOLD`, `CLINICAL_HOLD`, `MAIN_MERGE_HOLD`. A ordem obrigatória permanece fonte oficial custodiada → hash e localizador → evidência atômica → claim candidato → revisão de aplicabilidade e direitos → revisor habilitado → aprovação do Kernel/WO → CI estrito → merge técnico → publicação clínica em gate separado.