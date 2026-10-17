# Agentes Grok Bot — Referência versionada

**Fonte canônica**: este repositório.  
Os agentes Grok Bot são orquestrados externamente; este arquivo registra papéis, regras e mapeamento para os contratos do Kernel.

## Mapeamento

| Agente Grok | Papel no Kernel | Pode escrever? | Reporta a |
|-------------|-----------------|----------------|-----------|
| Arquiteto de Repositório | Implementação de controles via branch+PR | Sim (via PR) | Grok Bot / Leivis |
| Auditor | Verificação de integridade e precisão | Não (só evidência) | Grok Bot |
| Extrator | Captura literal de fontes oficiais | Staging apenas | Grok Bot |
| Atomizador | Transformação em átomos | Staging apenas | Grok Bot |
| Organizador do Drive | Organização privada | Não publica | Grok Bot |
| Inspetor de Qualidade | Resolução de pendências | Staging + recomendação | Grok Bot |
| BO-COSO / BO-COBIT / BO-ENF | Desenho e implementação de controles | Rascunho + PR | Tríade + Grok Bot |

## Regras invioláveis (determinísticas)

1. Toda alteração no repositório passa por branch + Pull Request. Nunca push direto na `main`.
2. Nenhum agente altera status de ato ou publica sem autorização explícita via Work Order.
3. O Kernel não pensa: só executa política versionada.
4. Evidência obrigatória: SHA-256, autor, agente_id e tipo de evento.
5. Fechado ≠ Publicado.

**Última atualização**: commit da Fase 2 (`c221521b`).
