# WO-05 — checkpoint de reconciliação da amostra 40/20 (17/11/2026)

**Estado:** `STRUCTURAL_QA_PASS_MAPPING_CANDIDATE`; **não** homologação clínica, trabalhista ou curricular. **EPIC:** #74, **PR:** #70. Leitura pelo conector GitHub da branch `review/cko-w7-public-evidence-20261114`.

## Insumos e rastreabilidade

- `market/JOB_DESCRIPTIONS_34_v0.5.7.jsonl` — 34 IDs, 14 especialidades; base imutável.
- `market/JOB_MARKET_INCREMENT_20261117_HEMODYNAMICS_TRANSPLANT_v0.1.0.json` — 2 anúncios, 2 especialidades candidatas; [commit 60057ab](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/60057ab92e22fac998c908f637a20d5e118929f9).
- `market/JOB_MARKET_INCREMENT_20261117_FOUR_SPECIALTIES_v0.1.0.json` — 4 anúncios, 4 especialidades candidatas; [commit 758f1c6](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/758f1c674918b86159ef09ba700586ac226cc77b).
- `specialties/COFEN_581_SPECIALTIES_65_AND_SUBAREAS_v0.5.0.jsonl` — catálogo canônico de 65 IDs; fonte normativa oficial https://www.cofen.gov.br/resolucao-cofen-no-581-2018/ (anexo consolidado, alterado até Decisão 21/2024).

## Testes estruturais executados (JS em memória sobre arquivos efetivamente lidos)

| ID | Verificação | Resultado |
|---|---|---|
| 01 | Baseline tem 34 anúncios | PASS |
| 02 | Primeiro delta tem 2 anúncios | PASS |
| 03 | Segundo delta tem 4 anúncios | PASS |
| 04 | Total consolidado tem 40 anúncios | PASS |
| 05 | 40 IDs de anúncio são distintos | PASS |
| 06 | Todos os IDs COFEN mapeados existem no catálogo de 65 | PASS |
| 07 | Exatamente 20 IDs COFEN distintos na amostra | PASS |
| 08 | Os seis IDs de especialidade dos deltas não constavam do baseline | PASS |
| 09 | Seis anúncios novos contêm URL HTTPS | PASS |
| 10 | Seis anúncios novos não inferem autorização clínica | PASS |
| 11 | Seis IDs COFEN dos deltas são distintos | PASS |

**11/11 PASS estruturais;** executados na leitura por conector, **não** como workflow de CI e **não** como revalidação ao vivo de páginas de vaga. A presença de URL não prova disponibilidade atual ou conteúdo integral. O catálogo COFEN foi confrontado com o anexo oficial, que distingue **III-02 Educação em Enfermagem** de **III-03 Educação Permanente e Continuada em Saúde**, e **I-33 Saúde Coletiva** de suas subáreas.

## Métricas por denominador

| Fase | Anúncios únicos | Especialidades / 65 | Cobertura |
|---|---:|---:|---:|
| Baseline | 34 | 14/65 | 21,54% |
| + Hemodinâmica/Transplante | 36 | 16/65 | 24,62% |
| + Assistência Domiciliária/Idoso/NEP/Saúde Coletiva | 40 | 20/65 | 30,77% |

Meta **de descoberta candidata** 20/65 atingida. **0/6** classificações novas com dupla revisão independente comprovada nesta rodada; nenhuma métrica de homologação pode ser derivada dos 11 testes estruturais. **45/65** especialidades ainda não representadas na amostra, não equivalendo a inexistência de vagas no mercado.

## Próxima fila P1 e critérios de aceite

Priorizar fontes primárias de empregador para especialidades ainda ausentes: `COFEN-581-I-03` (Acesso Vascular e Terapia Infusional), `COFEN-581-I-11` (Dermatológica/Feridas), `COFEN-581-I-12` (Diagnóstico por Imagens), `COFEN-581-I-20` (Hematologia) e `COFEN-581-I-21` (Hemoterapia). **São alvos de pesquisa, não vagas encontradas.** Validar job ID, empregador, conteúdo observável, data/status, não duplicação e separação entre exigência/preferência/atividade. Conferir independentemente o enquadramento de `III-03` e `I-33` antes de promover.

**HOLDs por objeto:** `HOLD_SOURCE` para URL ou requisitos indisponíveis, `HOLD_HUMAN` para dupla classificação, `HOLD_RIGHTS` para reutilização de texto integral. Outros objetos podem avançar. Sem alteração da main, Supabase, produção ou publicação clínica.

## CI do commit 758f1c6 (consultado nesta rodada)

- [CKO Curriculum and Market Read-only Audit — PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44089023483)
- [Pipeline Determinístico — PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44089023476)
- [CI — Validação — PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44089023544)
- [Canonical repository invariants — FAIL](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44089023673)

O resultado canônico permanece bloqueante **para integração**, não para descoberta e documentação de vagas. Não atribuir os 22 bloqueios históricos à presente amostra nem declarar sua resolução.
