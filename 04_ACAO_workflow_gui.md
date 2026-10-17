# ACÃO 04 — Criar drive-recursive-collect.yml via GitHub UI

## O que fazer

1. Ir em: https://github.com/IndiciumFIN/calculadorasdeenfermagem → aba **Actions** → **New workflow**
2. Ou: `.github/workflows/` → **Add file** → **Create new file**
3. Nome do arquivo: `drive-recursive-collect.yml`
4. Copiar conteúdo de: `/workspace/from_branches/.github/workflows/drive-recursive-collect.yml`

## Conteúdo esperado

```yaml
name: Drive recursive metadata collection
on:
  push:
    branches: [main]
    paths:
      - packages/cli/drive_recursive_inventory.py
      - config/drive_inventory_roots_*.json
      - tests/test_drive_recursive_inventory.py
      - .github/workflows/drive-recursive-collect.yml
  workflow_dispatch:
permissions:
  contents: read
jobs:
  collect:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.CLONE_PAT }}
          fetch-depth: 1
      - name: Python
        uses: actions/setup-python@...
        with:
          python-version: "3.11"
      - name: Tests
        run: |
          python -m pip install pytest
          PYTHONPATH=. python -m pytest tests/test_drive_recursive_inventory.py -q
      - name: Require credential
        env:
          GDRIVE_SA_KEY: ${{ secrets.GDRIVE_SA_KEY }}
          DRIVE_ACCESS_TOKEN: ${{ secrets.DRIVE_ACCESS_TOKEN }}
        run: |
          if [ -z "$GDRIVE_SA_KEY" ] && [ -z "$DRIVE_ACCESS_TOKEN" ]; then
            echo "::error::Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured"
            exit 2
          fi
      - name: Install SA deps
        env:
          GDRIVE_SA_KEY: ${{ secrets.GDRIVE_SA_KEY }}
        run: |
          if [ -n "$GDRIVE_SA_KEY" ]; then
            python -m pip install -r packages/cli/requirements.txt
          fi
      - name: Collect
        env:
          GDRIVE_SA_KEY: ${{ secrets.GDRIVE_SA_KEY }}
          DRIVE_ACCESS_TOKEN: ${{ secrets.DRIVE_ACCESS_TOKEN }}
        run: |
          python -m packages.cli.drive_recursive_inventory --roots config/drive_inventory_roots_20261016.json --output data/grc/evidencias/drive_recursive_candidate.json
      - name: Upload
        uses: actions/upload-artifact@...
        with:
          name: drive-recursive-candidate
          path: data/grc/evidencias/drive_recursive_candidate.json
          retention-days: 30
```

5. Clicar **"Commit directly to main"**
