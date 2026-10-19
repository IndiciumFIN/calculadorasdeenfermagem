# P3-B — Auditoria estática dos registros de validadores (candidato)
**Corte:** 2026-10-19 · **Estado:** OBSERVATION_CONFIRMED_IN_SOURCE / RUNTIME_UNTESTED / NO_KERNEL_ADMISSION. Sem modificação de código-fonte.

## Fonte por Git blob
- `main:packages/cli/kernel/core.py` — `7649f6e1f0160184e1014308cc05c90a5eb659e9`
- `main:packages/cli/validators/registry.py` — `e03e88a0ebe1179448883b7567d59e47193e3bd0`
- `main:packages/cli/validators/sha256_validator.py` — `f14906023a35adddb23dfc34bc9942ededf0ad33`
- `main:packages/cli/kernel/policy_registry.py` — `041bfaf4151effd05de7cb33a5458a53a2ab04af`

## Achados de inspeção
1. `core.py` declara seu próprio `VALIDATORS = {}`. `_lazy_import_validators()` usa `from validators import (Sha256Validator, NormAtomIdValidator, ..., cid10_validator, ...)` e devolve `locals()`. `_ensure_validators()` só copia entradas cujos nomes terminam em `_validator` **e** cujo objeto possui `validate`. Há risco de as classes com nomes em CamelCase e módulos de domínio não serem incluídos no dicionário local, mesmo que tenham sido registrados pelo decorador em outro lugar.
2. `validators/registry.py` mantém outro `VALIDATORS` preenchido por `@register`; `sha256_validator.py` usa o decorador. **Não foi localizado vínculo explícito entre o dicionário local de core e o registro central nesse trecho.** Isto é um problema verificável de desenho/integração a testar; não alegar falha runtime sem executar.
3. `Sha256Validator.validate` verifica o formato de 64 caracteres hexadecimais, mas **não compara digest com os bytes de origem**. Adequado para teste sintático; insuficiente isoladamente para integridade de corpus.
4. `PolicyRegistry._load_all` contém `except (json.JSONDecodeError, TypeError, FileNotFoundError): pass`, descartando alguns erros silenciosamente. Não inferir autorização positiva nem segurança operacional sem testes de falha.
5. A WO CE04 continua `DRAFT_NOT_ADMITTED` por readback anterior. A presença de política e classe não equivale a admissão.

## Casos mínimos a executar sob tarefa e gate aplicáveis
| Case | Entrada | Resultado esperado |
|---|---|---|
| REG-01 | Política válida usando `sha256_validator` | Validador concreto localizado e executado, sem fallback permissivo |
| REG-02 | Nome de validador inexistente | DENY com motivo e exit code válido |
| REG-03 | Validador somente no registry por decorador | Kernel deve encontrá-lo, ou registrar deficiência sem aprovar |
| REG-04 | SHA256 sintaticamente válido, mas conteúdo alterado | Teste de integridade de bytes separado rejeita |
| REG-05 | Política JSON inválida | DENY e diagnóstico rastreável |
| REG-06 | WO sem receipt ou com SHA alterado | DENY de execução produtiva |
| REG-07 | Import dos módulos em ambiente limpo | Sem erro de pacote; registrar exit code real |
| REG-08 | Stub/simulação `SUCCESS` | Não aceitar como Kernel real |

**Status dos testes:** NOT_EXECUTED_IN_THIS_MICROLOT. Vincular a FIND histórico de validator registry, quando identidade/proveniência permitir; se nova causa for provada, propor FIND sob governança, evitando duplicatas. Correções exigem FIND → política → validador → tarefa → WO → admissão Kernel → implementação isolada → testes adversariais → auditoria → promoção autorizada.

**Continuidade:** P3-A/P3-B ainda abertos; 12 tarefas originais inalteradas, POST-001 no final, 8/8 gates finais HOLD; no-change main/Supabase/Drive.
