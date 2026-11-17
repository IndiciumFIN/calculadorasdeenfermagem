# WO-05 — reconciliação completa dos incrementos 41/21 — 17/11/2026

**Estado:** STRUCTURAL_QA_PASS_MAPPING_CANDIDATE | **Issue:** #74 | **PR:** #70 | **escopo:** somente dados candidatos, sem homologação.

## Fontes lidas na branch de revisão pelo conector GitHub

1. `market/JOB_DESCRIPTIONS_34_v0.5.7.jsonl`: 34 anúncios únicos; 14 IDs COFEN principais.
2. `market/JOB_MARKET_INCREMENT_20261117_HEMODYNAMICS_TRANSPLANT_v0.1.0.json`: 2 anúncios (12764963, 12180487).
3. `market/JOB_MARKET_INCREMENT_20261117_FOUR_SPECIALTIES_v0.1.0.json`: 4 anúncios (12628161, 12836199, 12824715, 12747760).
4. `market/JOB_MARKET_INCREMENT_20261117_DIAGNOSTICO_IMAGEM_v0.1.0.json`: 1 anúncio (12808027), Rede D'Or / São Luiz Morumbi, [URL de origem](https://rededor.gupy.io/jobs/12808027), candidata à `COFEN-581-I-12`.
5. `specialties/COFEN_581_SPECIALTIES_65_AND_SUBAREAS_v0.5.0.jsonl`: 65 especialidades principais, com [fonte Cofen](https://www.cofen.gov.br/resolucao-cofen-no-581-2018/).

## Testes determinísticos executados nesta rodada

Em memória JS, sobre os **conteúdos completos dos cinco arquivos acima**, sem modificar a base:

| Teste | Resultado |
|---|---|
| Baseline com exatamente 34 registros | PASS |
| Catálogo com exatamente 65 especialidades principais | PASS |
| Incrementos anteriores com 2 e 4 anúncios | PASS |
| Incremento SADT com 1 anúncio identificado | PASS |
| 41 anúncios após união dos 4 conjuntos | PASS |
| 41 IDs de anúncios únicos | PASS |
| Todos os 41 vínculos COFEN constam do catálogo | PASS |
| Exatamente 21 especialidades principais distintas | PASS |
| I-12 não constava entre as 20 especialidades anteriores | PASS |
| Job 12808027 não constava entre os 40 anúncios anteriores | PASS |
| Sete URLs HTTPS nos deltas | PASS |
| Subárea `COFEN-581-I-12-02` não contabilizada como especialidade principal adicional | PASS |
| Nenhum dos sete incrementos declara autorização clínica | PASS |

**13/13 PASS estruturais executados via conector/JS, não GitHub Actions.** Não há rechecagem ao vivo do conteúdo das sete páginas nesta execução; acessibilidade atual e inscrição aberta não foram demonstradas. Verificação de integridade não equivale à revisão independente de competências.

## Resultado e denominadores

| Fase | Anúncios únicos | Especialidades candidatas | Cobertura |
|---|---:|---:|---:|
| Baseline | 34 | 14/65 | 21,54% |
| Após 2 incrementos | 36 | 16/65 | 24,62% |
| Após 4 incrementos | 40 | 20/65 | 30,77% |
| Após SADT/RM reconciliado | **41** | **21/65** | **32,31%** |

Meta diária de **20/65 superada em +1 especialidade**. Restam **44/65 sem anúncio nesta amostra**, o que não prova inexistência de vagas. A amostra é não probabilística; não estimar demanda nacional. **0/7 novas classificações** com revisão independente comprovada; todas seguem candidatas. Banco de talentos onco-hematologia `11022140` permanece fora da contagem de vagas por regra específica; não somar ao total de 41.

## Gates, decisões e próximos passos

- `PASS_STRUCTURAL` para unicidade, cardinalidade e correspondência de IDs COFEN; **não** para publicação ou homologação.
- `HOLD_HUMAN` para segunda revisão dos 7 vínculos, especialmente `III-03` (NEP) e `I-33` (APS/ESF) e enquadramento `I-12` (SADT RM).
- `HOLD_SOURCE` apenas para rechecagem de conteúdo/inscrições ao vivo, não para pesquisas independentes.
- `HOLD_RIGHTS` para reprodução de descrição integral de vaga; preservar apenas URL e rótulos independentes.
- Próxima busca P1: acesso vascular/infusão `I-03`, dermatologia `I-11`, hematologia `I-20`, hemoterapia `I-21`; somente adicionar vaga real com ID, empregador, evidência e dedup.
- Invariantes canônicos permanecem em FAIL e impedem integração; não confundir com os 13 testes desta amostra.

**Proibido:** merge main, Supabase DDL/DML, publicação clínica, declarar habilitação profissional. Baseline original de 34 preservado.
