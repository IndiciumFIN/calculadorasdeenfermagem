# Fábrica de Produção Determinística

## Decisão arquitetural

Não depender de agentes ou IA para compor materiais. O Builder usa biblioteca de camadas homologadas e contratos. IA só é usada (se necessário) na criação inicial de um modelo. Depois, o Builder produz variações sem consultar modelo novamente.

## Níveis de documentação

| Nível | Documento | Status |
|-------|-----------|--------|
| L0 | Identidade visual oficial (tokens) | Implementado |
| L1 | Biblioteca de camadas | Esqueleto criado |
| L2 | Catálogo de produtos | Pendente |
| L3 | Contrato de tarefa | Schema criado |
| L4 | Protocolo de validação | Pendente |

## Fluxo

1. Usuário escolhe camadas (pode omitir qualquer uma marcada como opcional).
2. Builder reorganiza a composição usando regras de espaçamento e alinhamento.
3. Exporta usando tokens oficiais.
4. Validação visual e editorial é humana antes de homologar o modelo.

## O que não é determinístico

- Redação criativa de conteúdo clínico novo.
- Julgamento estético final.
- Traduções sem revisão.

Esses itens exigem revisão humana e não são decididos por agente.
