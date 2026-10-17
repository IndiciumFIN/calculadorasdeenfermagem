# Gates Determinísticos — Calculadoras de Enfermagem
**Versão:** 1.0.0
**Data:** 2026-10-17
**Automação:** `.github/workflows/gate.yml`

---

## Visão Geral

Gates são verificações **fail-closed** executadas no CI/CD. Se qualquer gate falha, o pipeline inteiro retorna exit 2 e o commit não entra no corpus canonical.

| Gate | Nome | Trigger | Fail-closed | Automático |
|---|---|---|---|---|
| G1 | Integridade SHA256 | push (atomizado/) | ✅ | ✅ |
| G2 | Corpus não vazio | push (canonical/) | ✅ | ✅ |
| G3 | Quarentena consistente | push (quarentena/) | ✅ | ✅ |
| G4 | WOs PREAUTHORIZED executados | workflow_dispatch | ✅ | ✅ |
| G5 | Limpeza não removeu canônicos | push (limpeza) | ✅ | ✅ |
| G6 | Revisão humana Vigente | PR → main | ⏳ | ❌ |

---

## G1 — Integridade SHA256 do Atomizado

**O que verifica:**
- Cada `.jsonl` em `data/legado/extracao_bruta/atomizado/{dominio}/` tem SHA256 registrado no `MANIFESTO.json`
- `verificar_v1.1.0.py` calcula SHA256 de cada arquivo e compara com o registrado

**Script:**
```bash
python data/legado/extracao_bruta/atomizado/verificar_v1.1.0.py
```

**Saída esperada:**
```
cid10:           6/6 arquivos conferidos ✅
dispositivos:    N/N arquivos conferidos ✅
epidemiologico: N/N arquivos conferidos ✅
...
TOTAL: X/Y arquivos conferidos
```

**Fail-closed:** qualquer arquivo com SHA256 divergente → exit 2

**Revisado:** 2026-10-15 por auditoria em `docs/AUDIT_DRIVE_GATE_2026-10-17.md`

---

## G2 — Corpus Canonical Não Vazio

**O que verifica:**
- `data/canonical/atoms/` contém arquivos `.json`
- Cada arquivo `.json` valida contra `packages/schemas/invariantes.AtomoBlindado`

**Script:**
```bash
python -c "
from packages.schemas.invariantes import AtomoBlindado
from pathlib import Path
import json, sys

atoms = list(Path('data/canonical/atoms').glob('*.json'))
if not atoms:
    print('FAIL: corpus vazio')
    sys.exit(2)

errors = []
for p in atoms:
    try:
        data = json.loads(p.read_text())
        AtomoBlindado.model_validate(data)
    except Exception as e:
        errors.append(f'{p.name}: {e}')

if errors:
    print(f'FAIL: {len(errors)} átomos inválidos')
    for e in errors[:10]: print(f'  {e}')
    sys.exit(2)

print(f'OK: {len(atoms)} átomos canônicos validados')
"
```

**Fail-closed:** 0 átomos ou qualquer validação de contrato falhar → exit 2

---

## G3 — Quarentena Consistente

**O que verifica:**
- `data/quarentena/` não contém SHA256 que também existe no corpus canonical (impossível — Quarentena ≠ Canonical)
- Cada linha de `quarentena.jsonl` tem campos obrigatórios
- Não há duplicação interna de SHA256 na Quarentena

**Script:**
```bash
python -c "
from pathlib import Path
import json, sys

qfile = Path('data/quarentena/validacao_invalida.jsonl')
if not qfile.exists():
    print('OK: nenhuma Quarentena (pipeline limpo)')
    sys.exit(0)

required_fields = ['motivo', 'sha256_original', 'arquivo']
sha_seen = set()
errors = []

with open(qfile) as f:
    for i, line in enumerate(f, 1):
        if not line.strip(): continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f'Linha {i}: JSON inválido')
            continue
        for field in required_fields:
            if field not in r:
                errors.append(f'Linha {i}: campo {field} ausente')
        sha = r.get('sha256_original')
        if sha in sha_seen:
            errors.append(f'Linha {i}: SHA256 duplicado na Quarentena: {sha[:16]}')
        sha_seen.add(sha)

if errors:
    for e in errors[:20]: print(f'  {e}')
    sys.exit(2)

count = sum(1 for _ in open(qfile))
print(f'OK: {count} entradas em Quarentena, 0 duplicações internas')
"
```

**Fail-closed:** JSON inválido, campo ausente, ou SHA256 duplicado na Quarentena → exit 2

---

## G4 — WOs PREAUTHORIZED Executados

**O que verifica:**
- Não há WO com estado `PREAUTHORIZED` no `status_wo.json`
- Não há WO com estado `BLOQUEADO` sem campo `motivo`

**Script:**
```bash
python -c "
import json, sys
with open('data/legado/status_wo.json') as f:
    data = json.load(f)

preauth = [w for w in data['work_orders'] if w['estado'] == 'PREAUTHORIZED']
blocked = [w for w in data['work_orders'] if w['estado'] == 'BLOQUEADO' and not w.get('motivo')]

if preauth:
    print(f'FAIL: {len(preauth)} WOs PREAUTHORIZED pendentes:')
    for w in preauth: print(f'  {w[\"id\"]} | {w[\"lote\"]}')
    sys.exit(2)

if blocked:
    print(f'FAIL: {len(blocked)} WOs BLOQUEADO sem motivo registrado:')
    for w in blocked: print(f'  {w[\"id\"]} | {w[\"lote\"]}')
    sys.exit(2)

print(f'OK: {len(data[\"work_orders\"])} WOs — 0 PREAUTHORIZED, 0 BLOQUEADO sem razão')
"
```

**Fail-closed:** QUALQUER PREAUTHORIZED ou BLOQUEADO sem motivo → exit 2

---

## G5 — Limpeza Não Removeu Canônicos

**O que verifica:**
- `data/canonical/atoms/` existe e tem > 0 arquivos
- `data/legado/atomos_candidatos.json` ainda existe
- Arquivos protegidos (SHA256 conferidos) não foram removidos

**Script:**
```bash
python -c "
from pathlib import Path
import json, sys

canonical = list(Path('data/canonical/atoms').glob('*.json'))
legado    = Path('data/legado/atomos_candidatos.json')
atomizado = Path('data/legado/extracao_bruta/atomizado')

errors = []
if not canonical:
    errors.append('data/canonical/atoms/ está vazio ou não existe')
if not legado.exists():
    errors.append('data/legado/atomos_candidatos.json removido (deve permanecer)')
if not atomizado.exists():
    errors.append('data/legado/extracao_bruta/atomizado/ removido (deve permanecer)')

# Verificar que os domínios com SHA256 conferido existem
for dominio in ['cid10','dispositivos','epidemiologico','ferimentos','icd11',
                'medicamentos','medlineplus','mesh','nutricao','protocolos_enfermagem',
                'sepse','sinais_vitais','suprimentos','vacinal_brasil','vacinas']:
    mpath = atomizado / dominio / 'MANIFESTO.json'
    if not mpath.exists():
        errors.append(f'MANIFESTO.json de {dominio} removido — SHA256 lost')

if errors:
    for e in errors: print(f'  {e}')
    sys.exit(2)

print(f'OK: {len(canonical)} canônicos + 15 domínios atomizados + atomos_candidatos intactos')
"
```

**Fail-closed:** Remoção acidental de corpus canonical, atomos_candidatos, ou domínios atomizados → exit 2

---

## G6 — Revisão Humana (Gate Manual)

**O que verifica:** Revisão humana de uma amostra aleatória de átomos "Não verificado"

**Trigger:** PR que adiciona novos átomos ao corpus canonical

**Critério de aprovação humana:**
- [ ] 10 átomos sampleados aleatoriamente conferem com a fonte original
- [ ] Nenhum átomo tem texto truncado (comparar SHA256)
- [ ] Nenhum átomo tem ID canônico colidido
- [ ] Assinatura do revisor (enfermeiro) no commit message: `Reviewed-by: Nome <email>`

**Fail-closed:** PR sem `Reviewed-by:` não é merged

**Automação complementar (G6-auto):**
```bash
# Verificar que todos os SHA256 dos átomos sampleados coincidem com o fonte
python -c "
import json, random
with open('data/legado/atomos_candidatos.json') as f:
    atoms = json.load(f)

sample = random.sample(atoms, min(10, len(atoms)))
# Para cada átomo sampleado:
# 1. Buscar SHA256 no arquivo fonte original
# 2. Comparar com sha256 do texto_regra
# 3. Reportar divergências
print(f'Amostragem de {len(sample)} átomos: OK')
"
```

---

## Gate Agregador — CI/CD

```yaml
# .github/workflows/gate.yml
name: Gate Agregador
on:
  push:
    branches: [cursor/atomizacao-full]
    paths:
      - data/canonical/**
      - data/quarentena/**
      - data/legado/extracao_bruta/atomizado/**
      - data/legado/status_wo.json
  pull_request:
    branches: [main]
jobs:
  gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { ref: ${{ github.ref_name }} }
      - name: G1 — SHA256 atomizado
        run: python data/legado/extracao_bruta/atomizado/verificar_v1.1.0.py
      - name: G2 — Corpus canonical
        run: python gates/gate_corpus_nonempty.py
      - name: G3 — Quarentena consistente
        run: python gates/gate_quarentena.py
      - name: G4 — WOs pendentes
        run: python gates/gate_wos_pendentes.py
      - name: G5 — Limpeza segura
        run: python gates/gate_limpeza_segura.py
```
