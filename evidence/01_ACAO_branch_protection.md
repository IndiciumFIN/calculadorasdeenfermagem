# ACÃO 01 — Ativar Branch Protection na main

## Passos (GitHub Web UI)

1. Abrir: https://github.com/IndiciumFIN/calculadorasdeenfermagem/settings/branches
2. Clicar **"Add branch protection rule"**
3. Preencher:

| Campo | Valor |
|---|---|
| Branch name pattern | `main` |
| ☑ Require pull request reviews before merging | ✔ |
| ☑ Require status checks to pass before merging | ✔ (depois de CI existir) |
| ☑ Require conversation resolution before merging | ✔ |
| ☑ Do not allow bypassing the above settings | ✔ |
| ☐ Allow force pushes | ✗ (desmarcar) |
| ☐ Allow deletions | ✗ (desmarcar) |

4. Clicar **"Create"**

## Por que isso importa

Sem branch protection, qualquer pessoa com push access pode sobrescrever `main` diretamente — sem PR, sem revisão, sem registro. O plano exige proteção ativa antes de qualquer promoção.

## Verificação

Após criar, volte em Settings → Branches e confirme que `main` aparece com 🛡️ Protected.
