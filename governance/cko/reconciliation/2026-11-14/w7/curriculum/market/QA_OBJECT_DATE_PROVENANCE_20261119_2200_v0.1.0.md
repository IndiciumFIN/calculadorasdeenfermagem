# WO-05 — auditoria de proveniência por objeto e reconciliação determinística (19/11/2026, 22h BRT)

**Escopo:** EPIC #74 / PR #70; candidato não homologado. **Método:** leitura integral via GitHub dos cinco arquivos versionados e teste JS em memória. Não houve consulta direta às páginas de empregadores nesta rodada; não se afirma que qualquer vaga esteja aberta.

## Entradas e identidade (blob Git)
- `market/JOB_DESCRIPTIONS_34_v0.5.7.jsonl`: `71333f600f633a9e8f41bed6a68da763efc82de5`
- `market/JOB_MARKET_INCREMENT_20261117_HEMODYNAMICS_TRANSPLANT_v0.1.0.json`: `855c143b705a0479e9de4d14a03a1646973fa1d1`
- `market/JOB_MARKET_INCREMENT_20261117_FOUR_SPECIALTIES_v0.1.0.json`: `884b00aca6f9e7d8c0a143ff7bb2ec384485286b`
- `market/JOB_MARKET_INCREMENT_20261117_DIAGNOSTICO_IMAGEM_v0.1.0.json`: `d08cbbd7576a7a79760658d55d2201d92258609f`
- `specialties/COFEN_581_SPECIALTIES_65_AND_SUBAREAS_v0.5.0.jsonl`: `a8995435564c8a6785a0568335626e4c2e07754f`

## Testes efetivamente executados
1. Parsing dos cinco arquivos: PASS.
2. Cardinalidade por conjunto: 34 + 2 + 4 + 1 = **41**: PASS.
3. Chave `job_id` globalmente distinta: **41/41**; zero colisões: PASS.
4. IDs de especialidades principais distintos: **21/65**, todos existentes no catálogo de **65**: PASS.
5. URL `https://` em **41/41** registros: PASS estrutural (não implica acessibilidade).
6. Distribuição de estado da baseline: **31 NOT_VERIFIED, 2 CLOSED, 1 TALENT_POOL**; **0/34** marcadas como abertas verificadas.
7. Checagem de campo temporal individual nos sete incrementos: **4/7 sem data própria** em `observed_on`, `posted_on`, `published_on` ou `retrieved_on`. Os arquivos contêm data coletiva de coleta; **não equivale automaticamente a observação individual rastreável**.

## Quatro objetos com lacuna de data individual
| job_id | Empregador | COFEN candidato | Fonte primária | Decisão |
|---|---|---|---|---|
| 12180487 | Rede D'Or / Itaim | I-06 | https://rededor.gupy.io/job/eyJqb2JJZCI6MTIxODA0ODcsInNvdXJjZSI6Imd1cHlfcG9ydGFsIn0%3D | `HOLD_SOURCE_DATE` — recuperar evidência individual de observação/publicação |
| 12836199 | Rast Saúde / URSI | I-37 | https://rastsvmvg.gupy.io/job/eyJqb2JJZCI6MTI4MzYxOTksInNvdXJjZSI6Imd1cHlfcG9ydGFsIn0%3D | `HOLD_SOURCE_DATE` |
| 12824715 | Instituto Mais Saúde / HRAS | III-03 | https://institutomaissaude.gupy.io/jobs/12824715 | `HOLD_SOURCE_DATE`; classificação NEP sujeita a segunda revisão |
| 12747760 | SPDM / Região Butantã | I-33 | https://rastsbutanta.gupy.io/job/eyJqb2JJZCI6MTI3NDc3NjAsInNvdXJjZSI6Imd1cHlfcG9ydGFsIn0%3D | `HOLD_SOURCE_DATE`; classificação APS/ESF sujeita a segunda revisão |

**Interpretação:** os quatro anúncios continuam no inventário **candidato histórico**, não são promovidos a `SOURCE_DATE_VERIFIED` nem `OPEN`. Não preencher datas retroativamente por suposição. Os outros três têm algum campo temporal individual, mas isso **não** comprova status de inscrições em 19/11.

## Checkpoint e fronteiras
- Baseline: **34 anúncios / 14 especialidades de 65 (21,54%)**.
- Candidatos reconciliados: **41 anúncios únicos / 21 de 65 (32,31%)**, meta de **20/65 (30,77%)** atingida **apenas estruturalmente**; 44 especialidades sem anúncio nesta amostra.
- Revisão independente dos sete novos vínculos: **0/7 comprovada**. A amostra não é probabilística e não sustenta inferência de demanda nacional.
- `HOLD_SOURCE_DATE` e `HOLD_HUMAN` são por objeto; `HOLD_RIGHTS` para reprodução de texto protegido. Não alterar contadores até nova evidência.
- **Não executado:** consulta web direta dos sete anúncios, verificação de status atual, revisão humana COFEN, teste de workflow para este documento, homologação de direitos. CI anterior não substitui esses testes.
- **Não autorizado:** merge na main, escrita Supabase, produção, publicação clínica ou bypass de gates.
