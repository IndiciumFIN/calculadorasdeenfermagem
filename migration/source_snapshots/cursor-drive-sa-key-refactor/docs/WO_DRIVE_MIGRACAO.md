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

## Bloqueio

Este arquivo não é uma Work Order do kernel. Não há `contracts/work_orders/WO-2026_10_15_0041.json` nem tarefa qualificada de migração. `scripts/migrar_drive.py` sai com código 2 e não cria diretório nem copia arquivo.

`scripts/drive_duplicidade_check.py` só lê. Conteúdo idêntico em caminhos diferentes fica como duplicata. O mesmo nome com hashes diferentes é conflito, sem escolha de lado, e o comando sai com código 2.
