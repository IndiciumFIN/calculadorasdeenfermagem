# ACÃO 02 — Criar CLONE_PAT Secret

## Por que é necessário

GitHub Actions usa `GITHUB_TOKEN` por padrão — mas ele **não consegue clonar repos privados** em Actions de outros repos. O workflow `drive-recursive-collect.yml` precisa de um PAT com scope `repo` para fazer checkout.

## Passos (GitHub Web UI)

1. Abrir: https://github.com/settings/tokens → **"Generate new token (classic)"**
2. Configurar:

| Campo | Valor |
|---|---|
| Note | `CLONE_PAT — CE migration` |
| Expiration | `90 days` (recomendado) |
| ☑ repo (todos) | ✔ |

3. Clicar **"Generate token"** — copiar o token imediatamente
4. Ir em: https://github.com/IndiciumFIN/calculadorasdeenfermagem/settings/secrets/actions → **"New repository secret"**
5. Nome: `CLONE_PAT`
6. Valor: colar o token gerado
7. Clicar **"Add secret"**

## Alternativa

Se preferir PAT com scope mínimo:

```
Scope: repo (full)  — ou —
Scope: repo:public_repo (se o repo fosse público, mas não é)
```

## Verificação

Após criar, o workflow `drive-recursive-collect.yml` vai usar automaticamente `${{ secrets.CLONE_PAT }}`.
