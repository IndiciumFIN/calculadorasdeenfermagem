# WO-05 — rechecagem de fontes primárias e deduplicação parcial (19/11/2026, 19h BRT)

Escopo: EPIC #74 / PR #70, **candidato, não homologado**. Fontes abertas novamente nesta rodada; não reproduzir textos integrais.

## Confronto real com baseline

Leitura direta na branch W7 de `market/JOB_DESCRIPTIONS_34_v0.5.7.jsonl`: **34 linhas, 34 job_ids distintos, 0 duplicatas internas**. IDs `12807899`, `12613410`, `12799190` e `12628161` **não estão nessa baseline**. Consulta ao histórico da issue #74 (56 comentários no momento da leitura): os quatro IDs já estão mencionados em comentários anteriores; **isto não prova ausência em todos os deltas de arquivos**. Portanto não promover os três novos para contador total sem inventário completo. `12628161` foi explicitamente sinalizado como repetido em comentário anterior.

## Rechecagem oficial por objeto

| Job ID | Fonte primária do empregador | Observação nesta rodada | Classificação COFEN candidata | Decisão |
|---|---|---|---|---|
| 12807899 | https://qualidadecps.gupy.io/jobs/12807899 | Página individual acessível; título **Enfermeiro**; publicação 29/10/2026; inscrições indicadas até 28/12/2026; gestão de equipe e indicadores de diagnóstico por imagem; formação superior e experiência no setor | `COFEN-581-I-12` | `SOURCE_VERIFIED_CANDIDATE`; abertura em tempo real não certificada; `HOLD_HUMAN` para equivalência curricular |
| 12613410 | https://rbdimagem.gupy.io/jobs/12613410 | Página individual acessível, título **Enfermeiro \| HGPV**, atuação em centros de bioimagem, COREN ativo e plantões; **página exibe “Applications closed”** em 19/11/2026 | `COFEN-581-I-12` | `SOURCE_VERIFIED_CLOSED`; manter apenas como evidência histórica de competências; **não contabilizar como vaga aberta** |
| 12799190 | https://rededor.gupy.io/jobs/12799190?jobBoardSource=gupy_public_page | Resultado indexado da página oficial contém cargo **Enfermeiro \| Educação Continuada \| Itaim**, graduação em Enfermagem, COREN ativo e experiência em treinamento; tentativa de abertura direta sem query resultou em erro | `COFEN-581-III-03` | `SOURCE_INDEXED_DIRECT_FETCH_ERROR`; `HOLD_SOURCE` para confirmação direta/estado atual; não declarar vaga ativa |
| 12628161 | https://fp.gupy.io/jobs/12628161 | Não reaberta nesta rodada; histórico registra o ID como previamente descoberto | `COFEN-581-I-05` | `HOLD_DEDUP`; não adicionar novamente |

**Proveniência de consulta:** pesquisa web nas páginas oficiais de recrutamento em 19/11/2026; resultado direto da RBD com indicador explícito de inscrições encerradas; página Qualidade CPS acessível e resultado indexado Rede D'Or; issue #74 e baseline GitHub relidos. Links acima são as fontes originais.

## Checkpoint quantitativo sem dupla contagem

- Baseline 15/11: **34 anúncios únicos; 14/65 = 21,54%**.
- Checkpoint histórico documentado 17/11: **41 anúncios candidatos; 21/65 = 32,31%**; meta **20/65 = 30,77%** superada **como candidata**, não homologada.
- Esta rodada: **+0 ao contador oficial**; não reconciliados todos os deltas 34→41, nem comprovado novo anúncio ativo. Amostra não probabilística, sem inferência nacional.
- Não confundir especialidade principal com subárea nem considerar job técnico como enfermeiro especialista.

## Testes executados e pendentes

**Executados:** parsing de 34 JSONL da baseline e checagem de unicidade; comparação de quatro IDs com baseline; busca de menções no histórico de 56 comentários; leitura de páginas oficiais e status de RBD. **Não executados:** dedup de todos os deltas em árvore, segunda classificação COFEN, validação jurídica, teste local/CI do presente commit, confirmação em tempo real da Rede D'Or. Gates `HOLD_SOURCE`, `HOLD_HUMAN`, `HOLD_RIGHTS` são por objeto; publicação clínica segue **NO-GO**.
