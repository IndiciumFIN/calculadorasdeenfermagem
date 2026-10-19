# CE — Execução local dos microagentes determinísticos
**Corte:** 2026-10-19. **Estado:** LOCAL_ISOLATED_EXECUTION_PASS / NONPRODUCTIVE / NO_KERNEL. Documentação somente na branch PMO; nenhuma admissão WO, CI remota, implantação ou alteração de produção alegada.

## Implementação temporária, não implantada
Caminhos locais desta sessão: `/mnt/data/ce_local_agents/agents.py`, `test_agents.py`, `evidence/*.json`. Código Python 3 com CLI offline e papéis `P1-HASH-INDEXER`, `P2-RECONCILER`, `P5-INDEPENDENT-AUDITOR`. Não replica a plataforma de agentes nem confere autoridade do Kernel.

## Execuções e resultados
- `python -m unittest -v` na pasta `ce_local_agents`: **8/8 PASS**, incluindo arquivos alterados, exclusivos, SHA, falha por diretório inexistente, symlink proibido e adulteração de resultado.
- `python -m unittest discover -v` em `ce_p3_patch`: **5/5 PASS**. São testes do loader candidato pré-existente.
- Inventário real da pasta local `ce_p3_patch`: **4 arquivos**, incluindo bytecode de cache.
- Inventário da pasta local `ce_local_agents` no cutoff anterior à escrita dos quatro relatórios JSON: **5 arquivos**, incluindo caches.
- Comparação por paths e SHA: **0 SAME_BYTES, 0 DIFFERENT_BYTES, 4 ONLY_A e 5 ONLY_B**. As pastas eram conjuntos de código distintos: não são universos equivalentes do acervo do projeto e não demonstram divergências ou perdas de fonte.
- Auditor local independente recomputou os itens e as contagens: `PASS_BOUNDED`, 9 registros.
- Limite: não foram executados agentes persistentes, agentes LLM de múltiplos modelos, contratos WO reais, Kernel, políticas produtivas, PostgreSQL, GitHub CI nem reconciliação de conteúdos originais.

## Protocolo de uso seguro
```sh
python agents.py inventory DIRETORIO --output inv.json
python agents.py reconcile inv_a.json inv_b.json --output diff.json
python agents.py audit inv_a.json inv_b.json diff.json --output audit.json
python -m unittest -v
```
Executar apenas sobre cópias locais não sensíveis, com hashes, estado de cutoff e direitos claros. A implementação local ainda não está versionada como código executável no GitHub; este relatório não transfere nem instala o runtime. Uma publicação de scripts em branch técnica só deve ocorrer pela cadeia FIND→política→validador→tarefa→WO→admissão→testes→auditoria e após direito de escrita aprovado.

## Continuidade e gates
É permitido **continuar inspeções e reconciliações locais não destrutivas** mediante arquivos disponíveis e autorizado escopo. A implantação produtiva permanece `HOLD`: G0 DRAFT_NOT_ADMITTED e nenhum receipt; regras do PMO continuam `PMO_TRUSTED=false`; oito gates finais HOLD; a fila imutável com POST-001 na cauda não foi alterada. A auditoria da função local não substitui auditoria organizacional independente.
