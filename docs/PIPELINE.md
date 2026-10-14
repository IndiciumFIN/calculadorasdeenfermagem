# Pipeline Blindado

```bash
# 1. Ingestão com allowlist de fontes, máscara auditável e hash duplo
python packages/cli/main.py ingest --source URL_OFICIAL_OU_ARQUIVO --output data/raw.json

# 2. Processamento (todas as linhas; omissão crítica bloqueia por padrão)
python packages/cli/main.py process --input data/raw.json --output data/atomos.json

# 3. Validação fail-closed (exit 2 para corpus vazio, omissão ou invariante)
python packages/cli/main.py validate --input data/atomos.json
```

## Controles ativos

- Allowlist de domínios oficiais: fora dela, `REFERENCE_ONLY` bloqueia a extração.
- Proveniência: original bruto preservado em `data/sources/` com `sha256_original`,
  `sha256_transformado` e diff da máscara (CPF, telefone, marcas d'água).
- Auditoria de omissão por átomo (contra a linha de origem) e por corpus
  (números do documento ausentes dos átomos). Bloqueia por padrão.
- Invariantes do contrato v1.2.0: `extra='forbid'`, termos opinativos proibidos,
  placeholder de fonte proibido, `Vigente` exige evidência e domínio oficial.
- Status inicial sempre `Não verificado` — vigência nunca é atribuída na extração.
- Exit code 2 em qualquer falha (fail-closed; corpus vazio não é sucesso).

## Execução de LLM

Toda chamada de modelo passa pela porta única `packages/cli/llm_runner.py`,
com Work Order pré-autorizada, prompt com hash conferido em
`prompts/manifest.json`, `model_id` pinado na allowlist do agente
(`agents/registry.json`), temperatura 0 e recertificação vigente. A saída
aterrissa em `data/raw_llm/` como candidata (estágio raw), nunca direto no corpus.

## Gates de CI

O workflow `gate.yml` executa `gates/aggregate.sh` — único check que deve ser
obrigatório no branch protection. Nenhum gate é opcional; falha, ausência ou
não execução reprovam. Ver `docs/GAP_REMEDIATION.md` para a rastreabilidade
completa e as ações manuais pendentes.
