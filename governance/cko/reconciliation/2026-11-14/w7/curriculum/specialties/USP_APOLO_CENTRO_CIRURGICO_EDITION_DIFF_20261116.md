# CKO W7 — diferença de edições USP Apolo: Centro Cirúrgico (16/11/2026)

**Status:** `CANDIDATE_METADATA_ONLY`; EPIC #74; WO-CKO-CURR-20261115-04 (P1); sem promoção semântica ou clínica.

## Identidades institucionais independentes

| ID oficial da atividade | Período da turma | CH | Vagas indicadas | Fonte primária |
|---|---|---:|---:|---|
| 92849 | 01/03/2020–28/02/2022 | 40 h | 3 | https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=92849 |
| 125923 | 01/03/2025–28/02/2027 | 80 h | 3 | https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=125923 |
| 122199 | 01/03/2024–01/03/2027 | 242 h | 35 | https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=122199 |
| 135580 | 01/03/2026–28/02/2031 | 710 h | 6 | https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=135580 |

**Achado material:** duas atividades intituladas *Centro Cirúrgico* (92849 e 125923) têm descrição temática semelhante, mas **IDs, períodos e cargas horárias distintos (40 vs. 80 horas)**. Não deduplicar por título/ementa; não somar horas de diferentes ofertas. As outras duas atividades compartilham o título, mas possuem escopos descritivos e cargas diferentes; instituição/programa-mãe não inferidos.

**Identidade sugerida:** `provider=USP_APOLO | cod_oferecimentoatv | start_date | end_date`; apenas chaves candidatas, sem alteração no modelo canônico. A oferta 133376, já registrada no inventário prioritário W7, é **outra atividade**: NEPE Centro Cirúrgico/CME (06/03/2025–28/02/2027, 960 h), com contexto específico de fissuras orofaciais, https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=133376 . Não fundir com nenhuma das quatro acima.

## Reconciliação e direitos

- **4 atividades oficiais com IDs diferentes verificadas nesta rodada; 2 ofertas homônimas comparadas diretamente; 0 programas canônicos criados ou mesclados.** Não contabilizar estas atividades como quatro especializações independentes, nem como quatro novos programas no inventário de 114.
- `COFEN-581-I-09` (Centro Cirúrgico) e `COFEN-581-I-08` (CME) são associações temáticas **candidatas**; não há equivalência profissional/competência homologada. Recuperação pós-anestésica não é inferida do título genérico.
- Foram indexados **metadados factuais mínimos e URLs**, não cópias de ementas ou bibliografias. Titularidade, licença de reprodução/adaptação/TDM e uso comercial: `HOLD_RIGHTS`. Leitura da página não equivale a autorização de reprodução.
- O curso/atividade-mãe e a edição acadêmica exata de cada oferta: `HOLD_SOURCE_PARENT_PROGRAM` até consulta de ficha completa do curso no Apolo. Aprovação de equivalência: `HOLD_HUMAN`.
- Fonte acessada via busca pública em 16/11/2026; não foram obtidos hashes dos bytes remotos. Snapshot técnico do conteúdo não congelado: `HOLD_SOURCE_SNAPSHOT`.

## Testes de consistência candidatos (reexecutáveis)

1. Chaves oficiais `92849,125923,122199,135580,133376` são cinco valores distintos.
2. `92849` tem CH 40; `125923` tem CH 80; diferença de 40 h, **não** alteração retroativa de uma mesma edição.
3. Todos os registros permanecem `CANDIDATE_METADATA_ONLY`; nenhum `PART_OF` aprovado.
4. Zero cópias integrais de terceiros e zero novos registros no inventário canônico de 114 programas.

**Próximo passo:** recuperar programa-mãe/edição de cada ID, verificar se alguma oferta já existe nos 114 programas, e registrar equivalências somente após revisão humana. CI anterior (não valida este commit): https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43897687450 .
