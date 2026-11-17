# Plano de execução automática — WO-05 mercado por especialidade — 17/11/2026

**EPIC:** #74 | **PR:** #70 | **branch:** review/cko-w7-public-evidence-20261114 | **escopo:** amostra de anúncios e crosswalk COFEN, não encerramento integral do EPIC.

## Baseline e metas com denominadores

- Baseline versionado: `JOB_DESCRIPTIONS_34_v0.5.7.jsonl`, 34 anúncios únicos, 14/65 especialidades = **21,54%**; 15 famílias de cargos. A amostra é **não probabilística**, sem inferência de demanda nacional.
- Incremento candidato [commit 60057ab](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/60057ab92e22fac998c908f637a20d5e118929f9): 2 anúncios novos, 2 especialidades ainda não cobertas; **36 anúncios candidatos, 16/65 = 24,62%**; dupla classificação ainda pendente.
- **Meta operacional para 17/11:** descobrir e validar como **candidatos rastreáveis** anúncios de pelo menos mais 4 especialidades principais não cobertas, alcançando **20/65 = 30,77%**. Não prometer 100% da amostra, do currículo ou do EPIC hoje.
- **Meta de qualidade:** 100% dos novos candidatos com URL original do empregador, ID único, data de observação, cargo, vínculo explícito ou justificado com ID COFEN, sinal de habilidade codificado sem cópia integral, status da oferta, regra de deduplicação e estado de revisão.

## Ciclo automático por hora (até o fechamento de hoje)

1. **Leitura real:** verificar issue #74, PR #70, Plano Mestre, EXECUTION_MANIFEST, baseline de 34 anúncios, último delta e CKO Curriculum and Market Read-only Audit; identificar novos commits e não repetir trabalho sem delta.
2. **Gap analysis:** construir conjunto dos 65 IDs oficiais da lista versionada e subtrair os 14 cobertos + os 2 candidatos. Escolher 4+ especialidades faltantes com vagas verificáveis, sem confundir subáreas e especialidades principais.
3. **Descoberta de fonte primária:** priorizar páginas de recrutamento do empregador (Gupy oficial, hospitais, redes e órgãos públicos); guardar URL, job ID, data da observação, status e requisitos. Se a página estiver indisponível, registrar `SOURCE_UNAVAILABLE` sem contar como verificada.
4. **Deduplicação:** chave `source_platform + employer + job_id` e verificação contra todos os 34 IDs e incrementos posteriores; normalizar URLs e nunca contar anúncios de um mesmo ID duas vezes. Guardar possível vaga multiespecialidade como 1 anúncio e vínculos separados, com justificativa.
5. **Codificação auditável:** separar `required`, `preferred`, `responsibilities`, `behavioral_explicit`; distinguir competência demandada de título reconhecido e de habilitação clínica. Não reproduzir textos integrais protegidos.
6. **Gate de candidato:** registrar arquivos de delta JSON/JSONL e crosswalk na branch de revisão; testes candidatos para unicidade, IDs COFEN existentes, URLs oficiais, percentuais, status, integridade de schema e contagem por especialidade. Não modificar baseline original sem reconciliação completa.
7. **Execução e evidência:** verificar CI real de cada SHA, jobs e erros; fazer commit apenas com delta substantivo e comentar issue #74 com SHA, URLs, novos IDs, resultados executados vs especificados e HOLDs por objeto. Sem evidência nova, não criar commit de status vazio.
8. **Checkpoint final 17/11:** publicar relatório de cobertura por especialidade, total de anúncios, pendências de verificação e fila priorizada de próximas especialidades. Reportar separadamente cobertura `observed_candidate` e `independently_reviewed`.

## Portões e critérios de aceite

**PASS de descoberta:** anúncio original acessível, ID e empregador identificados, não duplicado, associação candidata ao ID COFEN justificada. **PASS de cobertura candidata:** ao menos 20 IDs distintos entre os 65, com 4 novos além dos 16 candidatos. **PASS de homologação:** segunda revisão independente + verificações automatizadas efetivamente executadas; não afirmar sem prova.

`HOLD_SOURCE` somente para fonte indisponível; `HOLD_HUMAN` somente para revisão de classificação; `HOLD_RIGHTS` somente para reutilização não autorizada; nenhum HOLD impede pesquisa de outras vagas. **PROIBIDO:** merge main, DDL/DML Supabase, publicação clínica, autorização de competência ou bypass de gates.

## Métricas de acompanhamento

| Métrica | Baseline | Candidato atual | Meta 17/11 |
|---|---:|---:|---:|
| Anúncios únicos | 34 | 36 | >=40, se 4 novas especialidades forem representadas por 4 anúncios distintos |
| Especialidades com pelo menos 1 anúncio | 14/65 | 16/65 | >=20/65 |
| Cobertura | 21,54% | 24,62% | >=30,77% |
| Especialidades novas além do candidato | 0 | 0 | >=4 |
| Testes executados sobre novo delta | Não confirmado | Não confirmado | executar quando houver runner disponível; registrar `NOT_RUN` caso contrário |

A automação deve **continuar após hoje** com o Plano Mestre geral; esta meta diária é um checkpoint, não um prazo para aprovar artificialmente dados.
