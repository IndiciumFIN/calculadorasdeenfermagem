# Status dos Jobs / Esteiras

**Nenhum job está homologado.**

| Job | Descrição | Status real | Evidência |
|-----|-----------|-------------|-----------|
| CLI ingest + process + validate | Pipeline local | Testado com amostra | Exit 0 e exit 2 reproduzidos |
| Registry local | Registro de itens | Funcional | JSON gerado |
| Esteira Drive (rclone + Python) | Pacote v0.1.0 | Auditado, falhas encontradas | 10/16 testes falharam na versão original |
| Agentes Supabase | Reconciliador + Auditor | Agendados | Teste de gravação confirmado |
| Agente ChatGPT PMO | Coordenador | Bloqueado por limite | Não ativo |
| PCNAC SOPs | Procedimentos | DRAFT | Somente documentação |

## Critério para homologar um job

1. Execução real em dados reais (ou amostra representativa).
2. Exit code 0 só quando todos os critérios obrigatórios passam.
3. Evidência independente (hash, contagem, auditoria).
4. Registro no Registry.
5. Revisão humana para conteúdo clínico/normativo.

Até lá, tudo permanece em `piloto` ou `documentado`.
