# Contratos dos Agentes — Calculadoras de Enfermagem

**Fonte canônica**: este repositório. Drive e conversas são subordinados.

## Agentes recuperados e suas responsabilidades

| Agente | Função | Entrada | Saída | Controle |
|--------|--------|---------|--------|----------|
| **Orquestrador** | Distribui tarefas, consolida evidências | Pedido humano | Status + evidência | Não publica |
| **Extrator** | Extração literal de fontes oficiais | URL / arquivo | Texto bruto + hash | Máscara obrigatória |
| **Atomizador** | Transforma em átomos | Texto limpo | JSON de átomos | Schema + invariantes |
| **Auditor** | Verifica fidelidade | Original + átomo | Relatório de omissão/alucinação | Camada 1 + 2 |
| **Pesquisador de Alterações** | Vigência e revogações | ID de norma | Status atualizado | Fonte oficial |
| **Organizador do Drive** | Inventário e quarentena | Pasta Drive | Relatório de duplicatas | Não exclui |
| **Inspetor de Qualidade** | Diagnóstico de pendências | Lote de átomos | Lista de FINDs | Evidência obrigatória |
| **Educação Continuada** | Aprendizado com falhas | FIND | Atualização de prompt/schema | Versionado |
| **Guardião** | Detecta inatividade e bloqueia criação desgovernada | Evento | Alerta + quarentena | Não publica |

## Regras invioláveis

1. Nenhum agente cria pasta ou arquivo no Drive sem consultar o Registry canônico.
2. Nenhum agente publica sem passar por `validate` (exit code 2).
3. Fechado ≠ Publicado. Estados separados.
4. Temperatura 0 em qualquer chamada de LLM.
5. Prompt versionado em `/prompts`. Nunca prompt livre.
6. Toda saída carrega hash, origem e versão de contrato.
