# Staging: normativos CLI local v0.6.0

**Estado:** `GITHUB_STAGING_ONLY`. Não está integrado ao Kernel oficial nem liberado para produção.

Este diretório contém **7 arquivos originais** da versão local v0.6.0, preservados byte a byte e comparados com seus Git blob SHA-1. O pacote local completo possui **46 arquivos**; os **39 restantes não foram enviados nesta etapa**. Portanto, `ce.py` e `run_windows.ps1` **não são executáveis isoladamente nesta branch**, pois dependem de `ce_local/` e `extensions/`.

## Controles

- WO local: `WO-LOCAL-GH-STAGE-20261016-001`, em `WO-GITHUB-STAGING.json`.
- Manifesto com SHA-256, Git blob SHA-1 e tamanho: `MANIFEST.json`.
- Testes realizados **no pacote completo local**, antes do staging: 75/75 `unittest` aprovados. Não são testes da branch parcial.
- Hash SHA-256 do ZIP completo local: `c488bee99257f9655a8f2bc5bd003128fcbe2ba5780d557f6c3d62c784a5dc8e`.
- GitHub: branch isolada de revisão; `main` intocada, sem merge.
- Drive, Supabase e front-end: não modificados.
- Validação pelo Kernel oficial: `NOT_SUBMITTED`.

## Gates ainda pendentes

1. Enviar os 39 arquivos restantes do pacote v0.6.0, sem incluir caches, credenciais, binários ou dados sensíveis.
2. Reexecutar testes e validações negativas na árvore completa do GitHub.
3. Qualificar WOs, procedimentos e validadores no Kernel oficial.
4. Validar a integridade dos normativos, a proveniência e os estados de HOLD antes de qualquer migração de conteúdo ou publicação.

**Atenção:** o manifesto descreve os 7 arquivos transferidos nesta etapa, não uma migração integral do corpus.
