# Template de FIND (Achado de Qualidade)

O registro executável está em `policies/finds.json` e `data/finds/registro.json`. Este modelo não abre, fecha nem autoriza correção.

```markdown
# FIND-XXX — [Título curto]

**Status**: Aberto | Em correção | Resolvido | Descartado  
**Severidade**: Crítica | Alta | Média | Baixa  
**Data**: AAAA-MM-DD  
**Agente que detectou**: [nome]  
**ID afetado**: NORM-XXXX

## Descrição
O que foi encontrado de errado.

## Evidência
Trecho original vs trecho gerado, ou hash, ou link.

## Impacto
O que pode quebrar se não corrigir.

## Ação recomendada
Passo concreto para resolver.

## Resolução
(Quando resolvido) O que foi feito e nova versão.
```
