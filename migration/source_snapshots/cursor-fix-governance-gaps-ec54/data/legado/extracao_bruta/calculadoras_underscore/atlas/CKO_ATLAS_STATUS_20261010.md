# CKO Atlas Anatômico 3D — situação verificável e perspectiva de entrega

**Referência:** 10/10/2026. **Ambiente:** Calculadoras de Enfermagem, projeto Supabase `pgsybzggewhinaniybiy` (Calculadoras-Smart). **Versão navegável mais recente recuperada:** `G4.3.3-lab`. **Escopo:** educacional; não é ferramenta de diagnóstico ou medição clínica.

## O que integra a entrega sem perda

1. **G3 — aquisição original:** os ZIPs oficiais BodyParts3D v4.0 OBJ_99, variantes **ISA** (2.234 OBJ) e **PART-OF** (1.258 OBJ); metadados TSV, scripts, manifests, PDFs/atribuições quando presentes no ZIP original. Esses 3.492 OBJ são *variantes de arquivo*, não 3.492 conceitos distintos. As fontes permanecem em um ZIP original, byte a byte, sem regravação.
2. **G3.6 — corpus canônico:** sete exportações JSONL com **65.200 registros atômicos**, assim distribuídos: 3.432 conceitos FMA, 4.273 representações BP, 47.492 relações FMA–FJ, 4.271 relações hierárquicas, 3.492 variantes de asset, 2.234 FJ geométricos distintos e 6 snapshots de fonte. SQLite, esquemas, relatórios e scripts permanecem dentro do ZIP original.
3. **G4.2 — base visual:** 3.432 conceitos pesquisáveis e 12 GLBs para quatro estruturas venosas; arquivos originais preservados byte a byte.
4. **G4.3.3 — última versão executável do laboratório:** interface Calculadoras de Enfermagem, logotipos enviados, navegação mobile, busca, favoritos, fichas, cinco categorias anatômicas, **474 FJ geométricos de 261 FMA distintos**, 27 GLBs derivados em grupos, JSONs por malha, carregamento incremental, créditos e scripts DeepSeek.
5. **Histórico:** G4.3, G4.3.1, G4.3.2, patches, candidato de interface e G4.4 de *diagnóstico*. **G4.4 não substitui a G4.3.3 executável**: é uma auditoria/recuperação dos estágios G0–G3.

## Estado de implementação e validação

| Linha | Situação em 10/10/2026 | Comprovação / ressalva |
|---|---|---|
| ZIPs históricos preservados | **PASS** | 15/15 ZIPs originais: CRC íntegro; hashes SHA-256 de cada ZIP no manifesto externo |
| Corpus original bruto | **PASS de arquivo** | 2.234 + 1.258 OBJ, cada ZIP interno passou CRC |
| Corpus canônico G3.6 | **PASS** | 7/7 JSONL SHA-256 coincidem; soma = 65.200 registros |
| Base G4.2 em G4.3.3 | **PASS** | 55/55 entradas ZIP comparadas por SHA-256, 0 alterações |
| Versão G4.3.3 | **PASS de integridade** | 693 arquivos do manifesto SHA-256 válidos, 0 divergências |
| Geometrias para interface G4.3.3 | **PARCIAL** | 474 FJ de 261 FMA; cinco grupos, não 5 sistemas totalmente completos |
| QA de interface G4.3.3 | **47/47 STATIC_PASS** | DOM, responsividade e renderizador simulado/fallback; NÃO comprova WebGL físico |
| QA WebGL real | **NÃO HOMOLOGADO** | Nenhum `runtime_webgl_verified=true` no registro do projeto |
| Traduções via API DeepSeek | **0 confirmadas** | Edge Function `cko-deepseek-gateway` v11 ACTIVE, `verify_jwt=true`, exige sessão owner/admin e opt-in de chamadas pagas; lote até 10 |
| Traduções pt-BR | **CANDIDATAS** | Terminologia em inglês e propostas não aprovadas; existe necessidade de revisar fila/hash, termos e nomenclatura |
| Storage Supabase | **NÃO PUBLICADO** | 0 arquivos `.obj`, `.glb`, `.gltf` encontrados em `storage.objects`; cópias estão nos pacotes locais |
| Direitos | **DOCUMENTADOS, NÃO COMPLETAMENTE LIBERADOS** | BodyParts3D informa CC BY 4.0; cabeçalhos históricos CC BY-SA 2.1 Japão foram preservados; verificar compatibilidade antes da distribuição pública final; materiais Z-Anatomy NC separados |
| Revisão especializada de anatomia | **PENDENTE** | Integridade e proveniência não substituem validação por especialista |
| Publicação de produção | **HOLD_PUBLICATION** | Nenhum novo release público verificado |

## PMO: números não intercambiáveis

- **Programa principal Atlas:** último checkpoint canônico **10/56 tarefas PASS (17,9%)**. Esse número é *histórico* e NÃO foi reavaliado contra todas as entregas G4.3.x; as outras 46 não devem ser declaradas concluídas sem reconciliação individual dos gates.
- **Aquisição G3:** 10/12 PASS (83,3%), restam WebGL/revisão anatômica e a conclusão documental/editorial.
- **Atomização G3.6:** 5/6 PASS (83,3%), última etapa de promoção controlada ao banco permanece separada e não autorizada automaticamente.
- **PMO técnico isolado `ce_atlas_dev.pmo_tasks` (consulta em 10/10/2026):** 22 tarefas: 12 `STATIC_PASS`, 3 `BLOCKED`, 4 `HOLD_HUMAN`, 1 `HOLD_PUBLICATION`, 2 `CODE_READY_NOT_RUNTIME_VALIDATED`. Esses estados não são somáveis ao PMO principal.

## Impeditivos para primeira publicação educacional

1. **WebGL real por dispositivo** com 474 FJ e subconjunto cardiovascular: renderização, interação, queda de contexto, uso de memória, desempenho e fallback.
2. **Revisão espacial e terminológica**, começando por coração e vasos; evitar inferir membros, lados e características apenas pelo nome genérico da malha.
3. **Estruturas cardiovasculares selecionadas e compostas** como módulo publicável: o coração `FMA7088` tem vínculos no corpus, mas não está homologado como um coração 3D completo na G4.3.3. É uma fase proposta, não lançada.
4. **Revisão e rastreabilidade de crédito/derivação** para o universo efetivamente publicado; revisar especialmente os avisos históricos e excluir arquivos terceiros restritos.
5. **Pipeline PT-BR**: gateway DeepSeek já ativo, mas sessão autenticada, lote inicial e revisão das saídas precisam ser executados. Não alterar IDs FMA, BP ou FJ.
6. **Staging seguro e observabilidade**, aprovação editorial, rollback e QA ponta a ponta. Sem publicar automaticamente.

## Caminho para uma entrega em fases

**Fase cardiovascular V1:** selecionar estruturas do coração e grandes vasos já presentes nos arquivos BodyParts3D; montagem anatômica auditável, seleção e fichas; usar só o acervo verificado, não os terceiros sob HOLD. **Marco de demonstração:** 7–12 dias úteis *estimados* com execução dedicada; **candidato publicável:** 3–5 semanas *estimadas*, condicionado a WebGL, revisão especializada, direitos e staging.

**Atlas multissistemas V1:** após a primeira liberação, reutilizar engine/UI e adicionar grupos anatomicamente coerentes, com QA e publicação por módulo. **Não** equiparar número de FJ convertido com cobertura total de qualquer sistema.

## Fontes de verdade e links

- PMO mestre: `cko_governance.documents.document_id = 'DOC-CKO-ATLAS-P04-PMO-20261010-v1.0.0'`, com deltas até `DOC-CKO-ATLAS-P04-PMO-DELTA-G25-20261010-v1.6.0`.
- G3 e G3.6 governança: documentos `DOC-CKO-ATLAS-G3-*`, `DOC-CKO-ATLAS-G36-*` no mesmo banco.
- PMO atual da frente: `ce_atlas_dev.pmo_tasks`, `ce_atlas_dev.qa_runs`, `ce_atlas_dev.asset_candidates`.
- Fontes oficiais: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html e https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
- Devido a preservação dos arquivos, todos os dados completos continuam disponíveis diretamente nos ZIPs originais e na origem institucional, não foram parafraseados nem sobrescritos para este arquivo de status.

**Atenção:** a integridade verificada garante igualdade de arquivos e consistência dos manifests conferidos; não prova correção pedagógica, anatômica, jurídica, desempenho de navegador nem integridade de um futuro upload. Rode `VERIFICAR_INTEGRIDADE.cmd` após a transferência.
