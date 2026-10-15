# Work Order — Migração do Drive com controle de duplicidades

**ID**: WO-2026_10_15_0041  
**Tipo**: corrigir-find  
**Autorizado por**: Leivis Lima  
**Estado**: PREAUTHORIZED

## Escopo

Converter a estrutura da pasta Drive `1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC` para o repositório, com atenção explícita a duplicidades.

## Condições de fail (obrigatórias)

| Condição | Ação |
|----------|------|
| Arquivo com mesmo SHA-256 já presente no repositório | Rejeitar (não sobrescrever) |
| Mesmo nome em pastas diferentes com conteúdo divergente | Quarentena + relatório |
| Ausência de hash de proveniência | Fail (exit 2) |
| Tentativa de promoção automática de status | Fail (exit 2) |
| Duplicata exata (mesmo conteúdo) | Deduplicar com registro |
| Duplicata com conteúdo diferente | Não escolher lado; quarentena |

## Processo

1. Listar conteúdo do Drive.
2. Calcular SHA-256 de cada arquivo.
3. Comparar com o repositório e com o inventário existente.
4. Gerar relatório de duplicidades.
5. Só então copiar o que for único e rastreável.

**Kernel só executa a política desta WO. Nenhuma promoção canônica automática.**
