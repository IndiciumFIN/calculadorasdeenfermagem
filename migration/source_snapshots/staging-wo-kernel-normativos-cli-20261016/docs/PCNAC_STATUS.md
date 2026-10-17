# PCNAC — Status real vs desejado (11/10/2026)

## Pacote analisado

`PCNAC_PROCEDIMENTOS_v0.1.0` contém 27 SOPs + Manual de índice.

**Status de todos os SOPs**: `DRAFT_NOT_IMPLEMENTED`

O próprio pacote declara:
> "criação documental não demonstra execução do pipeline, aprovação humana nem conformidade integral."

## O que já existe e funciona no repositório

| Camada | Implementado | Testado | Homologado |
|--------|--------------|---------|------------|
| Máscara (CPF, telefone) | Sim | Sim | Não |
| Auditoria de omissão de números | Sim | Sim | Não |
| Invariantes Pydantic (validate) | Sim | Sim | Não |
| Exit code 2 em falha | Sim | Sim | Não |
| Registry local (JSON) | Sim | Parcial | Não |
| Schema Supabase (registry) | Sim (migration) | Não | Não |

## Gates do PCNAC que fazem sentido agora

| Gate | Nome | O que já temos | O que falta para homologar |
|------|------|-----------------|---------------------------|
| G2 | Bytes recuperáveis + SHA-256 | Hash no CLI | Teste real com Drive |
| G4–G5 | Parsing controlado | Extrator simples | Adaptadores PDF/HTML reais |
| G11 | Validação estrutural | Invariantes + auditoria | Revisão humana |
| G12 | Revisão humana | Template FIND | Processo definido e executado |

## Regra que estamos aplicando

Nenhum job é declarado "homologado" sem:
1. Execução real (não só documentada).
2. Evidência de saída (hash, JSON, exit code).
3. Controles em sequência que pegam falhas.
4. Registro no Registry.

## Próximo passo concreto

1. Rodar o piloto da Resolução COFEN 736/2024 pela CLI.
2. Registrar no Registry com status `validado`.
3. Só então marcar o SOP correspondente como "executado em piloto".
4. Não promover nada a "homologado" sem revisão humana.
