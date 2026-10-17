# FIND-CE-G0-011 — Autoridade documental das Work Orders

**Status:** Aberto (OPEN) — sem admissão do Kernel
**Severidade:** Alta
**Data:** 2026-10-17
**Detecção:** Revisão de governança CE-G0; correção expressa do proprietário
**Escopo:** Calculadoras de Enfermagem / CE-00–CE-06

## Descrição
O planejamento anterior tratou o Supabase como possível origem de criação das Work Orders (WOs). O proprietário esclareceu que **as WOs são criadas e versionadas no repositório GitHub**. Confundir autoridade documental e estado transacional compromete rastreabilidade e pode gerar WOs concorrentes.

## Evidência
- Diretriz expressa do proprietário em 2026-10-17: «as WO são criadas no repositorio, nao no supabase».
- Contrato existente `contracts/policies/KERNEL-POLICY-001.json`: `wo_required=true`, `wo_template=data/legado/autorizacao_WO-{id}.json`.
- `docs/KERNEL.md`: políticas e contratos versionados em Git; Kernel executa políticas, não as cria.

## Impacto
Duplicação de autoridade, admissão presumida, execução sem WO versionada e perda de vínculo entre commit, política, validador, tarefa e decisão do Kernel.

## Ação corretiva proposta (não executada)
1. Inventariar os contratos reais de WO e as políticas aplicáveis na branch canônica.
2. Ajustar/criar política e validador específicos por alteração controlada, com testes positivos e negativos.
3. Criar tarefa determinística e WO **no GitHub**, vinculadas a este FIND e ao SHA-base.
4. Submeter a WO à admissão verificável do Kernel, com evidência de decisão e versão.
5. Somente após admissão, corrigir em branch isolada, testar, auditar e promover mediante autorização.
6. Registrar no Supabase apenas estado/eventos transacionais quando previsto no contrato; não criar WO concorrente.

## Critérios de encerramento
- Política, schema e validador verificados; testes reais PASS.
- WO versionada no GitHub e admitida pelo Kernel com readback auditável.
- Testes de integração e auditoria independente PASS; documentação e aprendizado atualizados.
- Sem conflitos de autoridade e sem aprovação presumida.

## Lições aprendidas
**Fonte documental ≠ autoridade de admissão ≠ estado de execução.** A WO nasce no GitHub; o Kernel admite ou rejeita; serviços transacionais podem registrar o estado sem substituir o artefato canônico. Não avançar por simples existência de arquivo ou status textual.

## Resolução
PENDENTE. Este FIND documenta a não conformidade, não a corrige nem constitui WO admitida.
