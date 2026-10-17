# Proteção de Agentes, LLMs e Operador

## Regras de ouro

1. **Nenhum agente publica direto**. Todo output passa por `validate` (exit code 2 se falhar).
2. **Temperatura 0** em qualquer chamada de LLM (quando implementada).
3. **Prompt fixo versionado** em `prompts/`. Nunca prompt livre no agente.
4. **Auditoria de omissão** antes de aceitar o átomo.
5. **Invariantes no código**, não só em documento.
6. **Fonte obrigatória** para status Vigente.
7. **Máscara** aplicada sempre na ingestão.

## O que isso impede

- Agente inventar prazo ou valor.
- Agente colocar termo opinativo.
- Publicar sem link da fonte.
- Dicionário desatualizado (quando rodar `generate_docs`).
- Extração de dados sensíveis desnecessários.

## Próximo passo recomendado

Implementar a camada 2 de auditoria (segundo modelo confrontando texto original vs átomo) e só então permitir o comando `publish`.
