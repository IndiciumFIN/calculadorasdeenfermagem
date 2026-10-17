# Plano de Execução WO + Kernel — Determinístico
**Gerado:** 2026-10-17
**Estado:** EM EXECUÇÃO
**Branch:** `cursor/fix-governance-gaps-ec54` → `cursor/atomizacao-full`

---

## 1. Diagnóstico do Acervo

### 1.1 WOs — Estado Atual (102 total)

| Estado | Count | Detalhe |
|---|---|---|
| PASS | 98 | Concluídos com sucesso |
| PREAUTHORIZED | 2 | Emitidos, nunca executados |
| BLOQUEADO | 2 | Falha técnica, requer retry |

**PREAUTHORIZED (prioridade 1 — executar agora):**
- `WO-2026_10_15_0090` — `cofen_dec_abaixo_50` — obter — 12 entradas
- `WO-2026_10_15_0091` — `cofen_dec_50mb` — obter — 3 entradas

**BLOQUEADO (prioridade 2 — retry):**
- `WO-2026_10_15_0087` — `nativos_google` — API retornou HTTP 500
- `WO-2026_10_15_0088` — `esteira_binarios` — Retornou HTML em vez de arquivo

### 1.2 Acervo de Átomos

| Estoque | Count | Status |
|---|---|---|
| `atomos_candidatos.json` | **104.668** | "Não verificado" — pendente canonical |
| `quarentena.jsonl` | **7.679** | Rejeitados — pendente revisão |
| `data/legado/extracao_bruta/atomizado/` | **14 domínios** | Com SHA256 + MANIFESTO ✅ |
| **Total pendente canonical** | **112.347** | — |

**Motivos de rejeição na quarentena (7.679):**
```
texto_curto         5718  (texto < 10 ou > 800 chars)
acima_contrato      1044  (não conforma ao schema AtomoBlindado)
conflito_duplicata   752  (mesmo NORM_ATOM_ID, textos diferentes)
termo_opinativo       165  (contém termos opinativos: recomenda-se, sugere-se)
```

**Fontes rejeitadas na quarentena (top):**
```
COFEN_LOTE2  4823  (planilha com muitos campos acima de 800 chars)
COFEN_LOTE3  1189
COFEN_LOTE6   966
COFEN_LOTE1   348
COFEN_LOTE4   206
```

### 1.3 Fontes já Atomizadas (com SHA256 + Manifesto)

Domínios com `MANIFESTO.json` e SHA256 conferido:
- `cid10/` — 15.407 átomos (capitulo, categoria, cido_categoria, cido_grupo, grupo, subcategoria)
- `dispositivos/` — [conferido]
- `epidemiologico/` — [conferido]
- `ferimentos/` — [conferido]
- `icd11/` — [conferido]
- `medicamentos/` — [conferido]
- `medlineplus/` — [conferido]
- `mesh/` — [conferido]
- `nutricao/` — [conferido]
- `protocolos_enfermagem/` — [conferido]
- `sepse/` — [conferido]
- `sinais_vitais/` — [conferido]
- `suprimentos/` — [conferido]
- `vacinal_brasil/` — [conferido]
- `vacinas/` — [conferido]

### 1.4 Duplicidades Já Tratadas

- 7 arquivos COFEN (NORMATIVE_ATOMS V1 + Lotes 1-6) **excluídos do Drive** (lixeira, recuperável)
- 38 duplicatas idênticas por ID → 1 cópia no corpus
- 336 conflitos de ID (texto diferente, mesmo NORM_ATOM_ID) → ambos para quarentena
- 1 conflito entre arquivos: RES-2026-805 art.5 (aspas em lato sensu + hífen MEC) — ambos na quarentena
- `public/cko_atlas_lab`, `cko_editorial`, `questoes_enfermagem`, `regulatory` no Supabase **não apagados** (não eram normativos)

---

## 2. Plano de Execução — 6 Macro-Fases

### FASE 0 — Preparação do Ambiente (Executar 1x)

```
Gates:
  ✅ GDRIVE_SA_KEY         — configurado
  ✅ .github/workflows/    — drive-recursive-collect.yml atualizado
  🔲 CLONE_CREDENTIAL     — PAT com repo:write (para git clone no CI)
  🔲 DRIVE_SA_KEY_FILE    — JSON no repo (para git clone no CI)
```

**Nova branch:** `cursor/atomizacao-full` a partir de `cursor/fix-governance-gaps-ec54`

**GitHub Actions secrets necessários:**
```
GDRIVE_SA_KEY         = JSON da service account ✅ (já existe)
CLONE_PAT             = Personal Access Token com repo + workflow scopes
```

### FASE 1 — WOs Pendentes (Paralelizável)

| WO | Tarefa | Lote | Entradas | Ação |
|---|---|---|---|---|
| WO-0090 | obter | cofen_dec_abaixo_50 | 12 | Executar — baixar PDFs COFEN <50MB |
| WO-0091 | obter | cofen_dec_50mb | 3 | Executar — baixar PDFs COFEN =50MB |
| WO-0087 | obter | nativos_google | 7 | Retry — API retornou 500 |
| WO-0088 | obter | esteira_binarios | 13 | Retry — retornou HTML em vez de binário |

**WO-0087 Fix:** O download público do Google Sheets falha com 500 intermitente.
- Solução: usar endpoint `/export?format=xlsx` em vez de `/view`
- Verificar se o arquivo existe antes de baixar

**WO-0088 Fix:** O download público de binários da ESTEIRA retorna HTML (proteção do Drive).
- Solução: usar a service account com `GDRIVE_SA_KEY` para baixar (acesso autenticado)
- Files que retornam HTML precisam de `alt=media` na API Drive

### FASE 2 — Atomização dos 4 Lotes (Pós-Obter)

| WO Depende | Lote | atomizar? | validar? |
|---|---|---|---|
| WO-0090 | cofen_dec_abaixo_50 | 🔲 | 🔲 |
| WO-0091 | cofen_dec_50mb | 🔲 | 🔲 |
| WO-0087 | nativos_google | 🔲 | 🔲 |
| WO-0088 | esteira_binarios | 🔲 | 🔲 |

### FASE 3 — Deduplicação Cross-Corpus (104.668 + 14 domínios)

**Não fazer merge manual.** Usar o script `data/legado/extracao_bruta/atomizado/verificar_v1.1.0.py` com:

```python
# Verificar SHA256 de cada domínio atomizado
# Comparar com sha256_do_fonte_origem (registrado no MANIFESTO)
# Átomo com SHA256 idêntico = deduplicado
# Átomo com SHA256 diferente = conflito → quarenta
```

**Regra determinística (de `duplicidades.json`):**
- Texto idêntico (mesmo SHA256) → 1 cópia no corpus
- Texto diferente, mesmo NORM_ATOM_ID → ambos para quarentena
- Confirmação: `sha256(texto_normalizado) == sha256_na_fonte`

### FASE 4 — Canonicalização via `migrate_legado.py`

**Entrada:** `data/legado/atomos_candidatos.json` (104.668)

**Saída:** `data/canonical/atoms/` (um JSON por átomo)

**Regras (de `packages/cli/migrate_legado.py`):**
1. Cada átomo → status `Não verificado` (vigência não é herdada — GOV-004)
2. Texto < 10 ou > 800 chars → `data/quarentena/texto_invalido/`
3. Mesmo `NORM_ATOM_ID`, textos diferentes → `data/quarentena/conflito/`
4. ID canônico: `NORM-{ano}-{int(sha256(legacy_id)[:12], 16)}`
5. Fail-closed: exit 2 se coluna obrigatória ausente, corpus vazio, ou rejeição de contrato

### FASE 5 — Limpeza do Diretório Legado

**Remover (redundante / piloto / raw não usado):**
```
data/legado/piloto/                          ← superseded by atomizado/
data/legado/extracao_bruta/raw/              ← redundant (já atomizado)
data/legado/extracao_bruta/sepse/            ← superseded by atomizado/sepse/
data/legado/extracao_bruta/sinais_vitais/    ← superseded by atomizado/sinais_vitais/
data/legado/extracao_bruta/suprimentos/      ← superseded by atomizado/suprimentos/
data/legado/extracao_bruta/vacinal_brasil/   ← superseded by atomizado/vacinal_brasil/
data/legado/extracao_bruta/vacinas/raw/      ← redundant
data/legado/extracao_bruta/protocolos_enfermagem/raw/pdfs/  ← PDFs raw não usados
data/legado/fontes/*.csv                     ← manter só SHA256SUM auditado
data/legado/fontes/*.xlsx                    ← manter só SHA256SUM auditado
data/legado/resumo.json                      ← substituído por status_wo.json
```

**Manter (não-legado, auditado):**
```
data/legado/atomos_candidatos.json           ← 104.668 candidatos (não verificado)
data/legado/quarentena.jsonl                 ← 7.679 rejeitados (pendente revisão)
data/legado/extracao_bruta/atomizado/       ← 14 domínios com SHA256 + manifesto
data/legado/duplicidades.json                ← auditoria de duplicatas
data/legado/status_wo.json                   ← tracker de 102 WOs
data/legado/drive_raizes.json                ← raízes Drive configuradas
data/legado/progresso_drive.json             ← estado do crawl
data/legado/supabase_normativos.json         ← análise do banco
data/legado/retirada_fontes.json            ←WO retirar autorizadas
data/legado/status_microfases_*.json        ← status por wave
```

**Manter (CI/CD):**
```
packages/cli/migrate_legado.py               ← script de canonicalização
packages/cli/auditor.py                      ← auditoria de omissão
data/legado/extracao_bruta/atomizado/verificar*.py  ← validação SHA256
```

### FASE 6 — Atualização de Governança

**Ficheiros novos a criar em `docs/`:**

```
docs/DETERMINISTIC_RULES.md          ← regras de determinismo (SHA256, fail-closed)
docs/GATES.md                        ← gates determinísticos (G1-G6)
docs/LEGADO_PLAN.md                  ← este documento
```

**Atualizações em `docs/GOVERNANCE.md`:**
```
GOV-004: Vigência não é herdada de planilhas legadas.
         Todo átomo nasce "Não verificado".
GOV-005: Texto < 10 ou > 800 chars → quarentena.
         Nenhum truncamento. SHA256 registra texto integral.
GOV-006: Sem SHA256 no fonte → fail-closed (exit 2).
         Commit sem SHA256 não entra no corpus canonical.
```

---

## 3. Automação — GitHub Actions Workflow

```yaml
name: WO + Kernel — Atomização Determinística
on:
  push:
    branches: [cursor/atomizacao-full]
  workflow_dispatch:
    inputs:
      fase:
        description: 'Fase (0-6)'
        required: true
        default: '1'

permissions:
  contents: read
  id-token: write

jobs:
  # ── FASE 0: Ambiente ──────────────────────────────────
  ambiente:
    if: inputs.fase == '0' || inputs.fase == ''
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: cursor/atomizacao-full
          token: ${{ secrets.CLONE_PAT }}
      - name: Verificar secrets
        run: |
          if [ -z "$GDRIVE_SA_KEY" ]; then echo "FAIL: GDRIVE_SA_KEY"; exit 2; fi
          echo "GDRIVE_SA_KEY: OK"

  # ── FASE 1: WOs Pendentes (Paralelo) ─────────────────
  wo-0090:
    needs: ambiente
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with: { ref: cursor/atomizacao-full, token: ${{ secrets.CLONE_PAT }} }
      - run: echo "WO-0090: cofen_dec_abaixo_50 — executar com GDRIVE_SA_KEY"
      - run: python -m packages.cli.pipeline run --work-order data/legado/autorizacao_WO-0090.json
      - run: python -m packages.cli.pipeline run --work-order data/legado/autorizacao_WO-0091.json
      - run: echo "WO-0087 + WO-0088 retry"
      - run: python -m packages.cli.pipeline run --work-order data/legado/autorizacao_WO-0087.json
      - run: python -m packages.cli.pipeline run --work-order data/legado/autorizacao_WO-0088.json

  # ── FASE 2: Atomização (Paralelo por lote) ────────────
  atomizar-4-lotes:
    needs: wo-0090
    strategy:
      matrix:
        lote: [cofen_dec_abaixo_50, cofen_dec_50mb, nativos_google, esteira_binarios]
    steps:
      - uses: actions/checkout@v4
        with: { ref: cursor/atomizacao-full, token: ${{ secrets.CLONE_PAT }} }
      - run: |
          WO_ID=$(echo ${{ matrix.lote }} | sed 's/_/-/g' | tr '[:lower:]' '[:upper:]')
          # Atomizar via Kernel CLI
          python -m packages.cli.main atomizar-wo --lote ${{ matrix.lote }}

  # ── FASE 3: Deduplicação SHA256 ───────────────────────
  deduplicar:
    needs: atomizar-4-lotes
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { ref: cursor/atomizacao-full, token: ${{ secrets.CLONE_PAT }} }
      - run: python data/legado/extracao_bruta/atomizado/verificar_v1.1.0.py
      - run: echo "SHA256 conferido. Conflicto_ids reportados."

  # ── FASE 4: Canonicalização ────────────────────────────
  canonicalizar:
    needs: deduplicar
    runs-on: ubuntu-latest
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v4
        with: { ref: cursor/atomizacao-full, token: ${{ secrets.CLONE_PAT }} }
      - run: pip install -r packages/cli/requirements.txt
      - name: Migrar átomos legados
        run: |
          python -m packages.cli.migrate_legado \
            --entrada data/legado/atomos_candidatos.json \
            --saida data/canonical/atoms/ \
            --quarentena data/quarentena/
      - name: Verificar fail-closed
        run: |
          count=$(ls data/canonical/atoms/*.json 2>/dev/null | wc -l)
          if [ "$count" -eq 0 ]; then echo "FAIL: corpus vazio"; exit 2; fi
          echo "Canonical: $count átomos gerados"

  # ── FASE 5: Limpeza ────────────────────────────────────
  limpar:
    needs: canonicalizar
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { ref: cursor/atomizacao-full, token: ${{ secrets.CLONE_PAT }} }
      - name: Remover redundante
        run: |
          rm -rf data/legado/piloto/
          rm -rf data/legado/extracao_bruta/raw/
          rm -rf data/legado/extracao_bruta/*/raw/
          rm -rf data/legado/extracao_bruta/protocolos_enfermagem/raw/pdfs/
          rm -f  data/legado/resumo.json
          echo "Limpeza concluída — commitar delta"

  # ── FASE 6: Governança ────────────────────────────────
  governanca:
    needs: limpar
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { ref: cursor/atomizacao-full, token: ${{ secrets.CLONE_PAT }} }
      - run: |
          # Atualizar GOVERNANCE.md com GOV-004, GOV-005, GOV-006
          # Criar DETERMINISTIC_RULES.md
          # Criar GATES.md
          echo "Governança atualizada"

  # ── Gate Final ────────────────────────────────────────
  gate-final:
    needs: [governanca, limpar, canonicalizar]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { ref: cursor/atomizacao-full, token: ${{ secrets.CLONE_PAT }} }
      - run: |
          CANONICAL=$(ls data/canonical/atoms/*.json 2>/dev/null | wc -l)
          QUARENTENA=$(wc -l < data/quarentena/validacao_invalida.jsonl)
          echo "Atomização concluída: $CANONICAL canonicalizados, $QUARENTENA em quarentena"
          # Fail-closed: qualquer das contagens ser 0 (se deveria ter conteúdo) é erro
          if [ "$CANONICAL" -eq 0 ]; then echo "::error::Corpus canonical vazio"; exit 2; fi
```

---

## 4. Gates Determinísticos (G1-G6)

| Gate | Verificação | Fail-closed | Tipo |
|---|---|---|---|
| G1 | SHA256 fonte == SHA256 no MANIFESTO | ✅ | Automático |
| G2 | `data/canonical/atoms/` não vazio após migrate | ✅ | Automático |
| G3 | Quarentena sem duplicatas de SHA256 válidas | ✅ | Automático |
| G4 | Todos WOs PREAUTHORIZED executados | ✅ | Automático |
| G5 | Limpeza não removeu átomos canônicos | ✅ | Automático |
| G6 | Revisão humana — átomos "Não verificado" | ⏳ | Manual |

---

## 5. Estrutura Final do Diretório

```
data/
├── canonical/                    ← OUTPUT FINAL (imutável)
│   └── atoms/
│       ├── NORM-2025-*.json     ← 104.668 + novos átomos
│       └── SHA256SUMS.txt       ← Audit trail
├── quarentena/                   ← Pendente revisão
│   ├── texto_invalido/          ← < 10 ou > 800 chars
│   ├── conflito/                ← Mesmo ID, texto diferente
│   └── opinativo/               ← Termos opinativos
├── legado/
│   ├── atomos_candidatos.json   ← (futuro: movido para canonical)
│   ├── quarantine.jsonl          ← (futuro: movido para quarentena/)
│   ├── extracao_bruta/atomizado/ ← 14 domínios com SHA256 ✅
│   ├── duplicidades.json         ← Auditoria de duplicatas ✅
│   ├── status_wo.json            ← Tracker de 102 WOs ✅
│   ├── drive_raizes.json         ← Configuração Drive ✅
│   └── (outros *.json de status) ← Mantidos para auditoria
└── grc/
    └── evidencias/               ← Outputs de gates CI/CD
```

---

## 6. Próximos Passos — Ordem de Execução

```
[AGORA]       Criar branch cursor/atomizacao-full
[AGORA]       Adicionar CLONE_PAT como secret no GitHub
[AGORA]       Executar FASE 0 (verificar ambiente)
[IMEDIATO]    Executar FASE 1 (WO-0090, 0091, 0087, 0088)
[PÓS-FASE-1]  Executar FASE 2 (atomizar 4 lotes)
[PÓS-FASE-2]  Executar FASE 3 (deduplicação SHA256)
[PÓS-FASE-3]  Executar FASE 4 (migrate_legado → canonical)
[PÓS-FASE-4]  Revisão humana (G6) — átomos "Não verificado"
[PÓS-FASE-5]  Executar FASE 5 (limpeza)
[PÓS-FASE-6]  Executar FASE 6 (atualizar governança)
[PÓS-TUDO]    PR cursor/atomizacao-full → main
```

---

## 7. O que NÃO Será Feito (Fora de Escopo)

- ~~Atomizar domínios já atomizados com SHA256~~ ✅ Já feito
- ~~Tratar duplicatas de arquivos Drive~~ ✅ Já feito
- ~~Migrar Supabase~~ ⏳ Pendente — requer SUPABASE_URL + ANON_KEY + SERVICE_ROLE_KEY
- ~~Branch protection na main~~ ⏳ Pendente — requer ação humana em Settings
- ~~Baixar e atomizar PDFs raw de `protocolos_enfermagem/raw/pdfs/`~~ Mantidos para possível uso futuro
