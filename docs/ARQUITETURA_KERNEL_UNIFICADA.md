# Arquitetura Kernel Unificada — v1.0.0
**Data:** 2026-10-17
**Princípio:** Sem política no Kernel → nada aprovado.

---

## 1. O que é o Kernel

O Kernel é um **registry de políticas + executor determinístico**. Tudo passa por ele.

```
INPUT → KERNEL → OUTPUT
         │
    ┌────┼────┐
    │    │    │
  POLÍ- VALI- FONTE
  TICA  DOR  (CONTRATO)
```

O Kernel **não pensa, não cria, não interpreta**. Ele só compara INPUT contra POLÍTICA. Se confere → APPROVED. Se não confere → REJECTED (exit 2).

---

## 2. Registry de Fontes — Contratos Formais

Cada fonte oficial tem um contrato版本锁定 no Git.

### 2.1 Fontes Identificadas

| Fonte | Tipo | Atualização | Parser | Status |
|---|---|---|---|---|
| COFEN (DOU) | Normativo | Sob demanda | `packages/cli/adapters/dou.py` | ✅ parser existente |
| ANVISA (RDC/IN/Port) | Normativo | Sob demanda | `packages/cli/adapters/dou.py` | ✅ parser existente |
| DOU Federal | Normativo | Sob demanda | `packages/cli/adapters/dou.py` | ✅ parser existente |
| CID-10 (DATASUS) | Classificação | Anual | `packages/cli/parsers/cid10.py` | 🔲 a criar |
| CID-11 (OMS) | Classificação | Anual | `packages/cli/parsers/icd11.py` | 🔲 a criar |
| MeSH (NLM) | Terminologia | Mensal | `packages/cli/parsers/mesh.py` | 🔲 a criar |
| Tabela TACO (UNICAMP) | Nutricional | Anual | `packages/cli/parsers/taco.py` | 🔲 a criar |
| Medicamentos ANVISA | Registro | Diário | `packages/cli/parsers/anvisa_med.py` | 🔲 a criar |
| Vacinas CDC (CVX) | Classificação | Sob demanda | `packages/cli/parsers/vacinas.py` | 🔲 a criar |
| CDSI (BR) | Calendário | Anual | `packages/cli/parsers/cdsi.py` | 🔲 a criar |
| ANVISA Dispositivos | Registro | Diário | `packages/cli/parsers/anvisa_dev.py` | 🔲 a criar |
| SINAN (MS) | Notificação | Diário | `packages/cli/parsers/sinan.py` | 🔲 a criar |
| PNI (MS) | Vacinal | Diário | `packages/cli/parsers/pni.py` | 🔲 a criar |
| CATMAT (Compras) | Suprimentos | Diário | `packages/cli/parsers/catmat.py` | 🔲 a criar |
| MedlinePlus | Educativo | Semanal | `packages/cli/parsers/medlineplus.py` | 🔲 a criar |
| FHIR R4 (LOINC) | Sinais Vitais | Sob demanda | `packages/cli/parsers/fhir.py` | 🔲 a criar |
| Atlas BodyParts3D | Anatômico | Estático | `packages/cli/parsers/atlas.py` | 🔲 a criar |
| OEBS (SIES) | Insumos | Diário | `packages/cli/parsers/sies.py` | 🔲 a criar |
| ESAVI (ANVISA) | Eventos | Diário | `packages/cli/parsers/esavi.py` | 🔲 a criar |
| Atlas Parts | Suprimentos | Estático | `packages/cli/parsers/atlas.py` | 🔲 a criar |

### 2.2 Contrato de Fonte

Cada fonte tem um arquivo `contracts/{fonte_slug}.json`:

```json
{
  "schema": "CE-FONTE-CONTRATO-1.0.0",
  "fonte_slug": "cid10",
  "fonte_oficial": "DATASUS/CID-10",
  "url_oficial": "https://datasus.saude.gov.br/",
  "tipo": "CLASSIFICACAO",
  "parser": "packages/cli/parsers/cid10.py",
  "parser_version": "1.0.0",
  "parser_hash": "sha256:abc123...",
  "campos_entidade": {
    "codigo": {"tipo": "string", "required": true, "pattern": "^[A-Z][0-9]{2}(\\.[0-9])?$"},
    "descricao": {"tipo": "string", "required": true, "min_length": 5},
    "capitulo": {"tipo": "string", "required": false}
  },
  "update_policy": {
    "trigger": "MANUAL",  // MANUAL | SCHEDULE | WEBHOOK
    "schedule": null,
    "last_update": "2026-01-01",
    "version_field": "versao"
  },
  "kernel_policy_required": true,
  "validator": "packages/cli/validators/cid10_validator.py",
  "validator_hash": "sha256:def456..."
}
```

---

## 3. Registry de Validadores — 1×1 Testados e Homologados

### 3.1 Validadores por Tipo de Dado

| Validador | Política | Testes | Homologado |
|---|---|---|---|
| `cnpj_validator` | regex + dígito verificador | 50 testes | 🔲 |
| `coren_validator` | formato + dígito UF | 30 testes | 🔲 |
| `norm_atom_id_validator` | `NORM-{ano}-{12hex}` | 20 testes | 🔲 |
| `sha256_validator` | 64 hex chars | 10 testes | 🔲 |
| `url_validator` | https + domínio allowlist | 15 testes | 🔲 |
| `texto_length_validator` | 10-800 chars | 20 testes | 🔲 |
| `codigo_atlas_validator` | formato ATLAS-XXX | 10 testes | 🔲 |
| `ncm_validator` | NCM 8 dígitos | 20 testes | 🔲 |
| `cid10_validator` | código CID-10 válido | 30 testes | 🔲 |
| `cid11_validator` | código CID-11 válido | 30 testes | 🔲 |
| `cvx_validator` | código CVX (vacinas) | 20 testes | 🔲 |
| `atomo_schema_validator` | `AtomoBlindado` pydantic | 50 testes | 🔲 |
| `escala_schema_validator` | `EscalaClinica` pydantic | 30 testes | 🔲 |
| `dispositivo_schema_validator` | `DispositivoMedico` pydantic | 20 testes | 🔲 |
| `jsonl_line_validator` | JSON válido por linha | 10 testes | 🔲 |
| `sha256_corpus_validator` | SHA256 confere com MANIFESTO | 20 testes | 🔲 |

### 3.2 Interface de Validador (contrato)

```python
# packages/cli/validators/base.py
from abc import ABC, abstractmethod

class BaseValidator(ABC):
    """Interface que todo validador deve implementar."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do validador (usado no report)."""
        ...
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versão do validador (hash do código)."""
        ...
    
    @abstractmethod
    def validate(self, item: dict) -> tuple[bool, str | None]:
        """
        Valida um item.
        Returns: (is_valid, error_message)
        """
        ...
    
    @abstractmethod
    def validate_batch(self, items: list[dict]) -> list[tuple[dict, bool, str | None]]:
        """
        Valida lote. Retorna (item, is_valid, error_message).
        """
        ...
    
    @abstractmethod
    def test_suite(self) -> list[tuple[dict, bool, str | None]]:
        """
        Retorna casos de teste: (input, expected_valid, description).
        Mínimo 10 casos: 5 válidos, 5 inválidos.
        """
        ...
    
    def run_tests(self) -> bool:
        """Executa test_suite. Fail-closed se qualquer teste falhar."""
        ...
```

### 3.3 Registro de Validadores

```python
# packages/cli/validators/registry.py
VALIDATORS: dict[str, BaseValidator] = {}

def register(cls: type[BaseValidator]):
    VALIDATORS[cls().name] = cls()

def get_validator(name: str) -> BaseValidator:
    if name not in VALIDATORS:
        raise ValueError(f"Validador '{name}' não registrado no Kernel.")
    return VALIDATORS[name]
```

---

## 4. Registry de Políticas do Kernel

### 4.1 Formato de Política

```json
{
  "schema": "CE-KERNEL-POLICY-1.0.0",
  "id": "KERNEL-POLICY-001",
  "name": "Normativo COFEN",
  "description": "Valida átomos de resoluções COFEN do DOU Federal",
  "source_contract": "contracts/cofen_dou.json",
  "validators": ["atomo_schema_validator", "norm_atom_id_validator", "texto_length_validator", "url_validator"],
  "atoms_output": "data/canonical/atoms/cofen/",
  "quarentena_output": "data/quarentena/cofen/",
  "sha256_required": true,
  "fail_closed": true,
  "requires_human_review": true,
  "review_policy": {
    "min_sample_size": 10,
    "approval_required": "enfermeiro_registrado",
    "reviewed_by_in_commit": true
  },
  "wo_required": true,
  "wo_template": "data/legado/autorizacao_WO-{id}.json",
  "updated_at": "2026-10-17T00:00:00Z"
}
```

### 4.2 Políticas por Domínio

| Política | Validadores | WO | Revisão Humana |
|---|---|---|---|
| `KERNEL-POLICY-001` Normativo COFEN | atomo + norm_id + length + url | ✅ | ✅ |
| `KERNEL-POLICY-002` Normativo ANVISA | atomo + norm_id + length + url | ✅ | ✅ |
| `KERNEL-POLICY-003` CID-10 | cid10 + schema | ✅ | ⏳ |
| `KERNEL-POLICY-004` CID-11 | cid11 + schema | ✅ | ⏳ |
| `KERNEL-POLICY-005` MeSH | mesh + schema | ✅ | ⏳ |
| `KERNEL-POLICY-006` Medicamentos ANVISA | schema + ncm | ✅ | ✅ |
| `KERNEL-POLICY-007` Vacinas CDC | cvx + schema | ✅ | ⏳ |
| `KERNEL-POLICY-008` Sinais Vitais FHIR | fhir + loinc | ✅ | ⏳ |
| `KERNEL-POLICY-009` Dispositivos ANVISA | anvisa_dev + schema | ✅ | ⏳ |
| `KERNEL-POLICY-010` Nutricional TACO | taco + schema | ✅ | ⏳ |
| `KERNEL-POLICY-011` Epidemiologia SINAN | sinan + schema | ✅ | ✅ |
| `KERNEL-POLICY-012` Vacinal PNI | pni + schema | ✅ | ⏳ |
| `KERNEL-POLICY-013` Suprimentos CATMAT | catmat + schema | ✅ | ⏳ |
| `KERNEL-POLICY-014` EAVI ANVISA | esavi + schema | ✅ | ⏳ |
| `KERNEL-POLICY-015` Educativo MedlinePlus | medlineplus + schema | ✅ | ⏳ |

---

## 5. CLI Universal — Um Comando por Política

```bash
# Estrutura
kernel <comando> --policy <policy-id> [opções]

# Comandos disponíveis
kernel ingest     --policy KERNEL-POLICY-001 --source DOU --date 2026-10-01
kernel atomize    --policy KERNEL-POLICY-001 --input data/raw/COFEN_RES_0800.pdf
kernel validate   --policy KERNEL-POLICY-001 --input data/canonical/atoms/cofen/
kernel quarantine --policy KERNEL-POLICY-001 --dry-run
kernel canonical  --policy KERNEL-POLICY-001 --input data/legado/atomos_candidatos.json
kernel update     --policy KERNEL-POLICY-003  # CID-10 update from DATASUS
kernel diff       --policy KERNEL-POLICY-003  # diff since last update
kernel report     --policy KERNEL-POLICY-001  # HTML report
kernel gate       --policy KERNEL-POLICY-001  # Run gate checks

# Sem --policy → lista políticas disponíveis
kernel list-policies
kernel show-policy KERNEL-POLICY-001
```

---

## 6. Workflow de Atualização Automática

Cada fonte com `update_policy.trigger = SCHEDULE` gera um workflow:

```yaml
# .github/workflows/update-cid10.yml
name: Update CID-10 (DATASUS)
on:
  schedule:
    - cron: '0 3 1 * *'   # 1º dia do mês, 03:00 UTC
  workflow_dispatch:
    inputs:
      force:
        description: 'Force update even if checksum unchanged'
        required: false
        type: boolean

jobs:
  update-cid10:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - name: Fetch CID-10
        run: python -m kernel update --policy KERNEL-POLICY-003
      - name: Validate
        run: python -m kernel validate --policy KERNEL-POLICY-003
      - name: Atomize
        run: python -m kernel atomize --policy KERNEL-POLICY-003
      - name: Gate
        run: python -m kernel gate --policy KERNEL-POLICY-003
      - name: Commit if changed
        run: |
          if git diff --quiet; then
            echo "No changes — skip commit"
          else
            git config user.name "kernel-agent"
            git config user.email "kernel@indiciumfin.com"
            git add data/canonical/atoms/cid10/
            git commit -m "chore(auto): CID-10 update $(date -u +%Y-%m-%d)"
          fi
```

---

## 7. Metamodelo de Dados — Schema Formal

### 7.1 Átomo Canônico

```json
{
  "schema": "CE-ATOMO-CANONICO-1.0.0",
  "id_atomo": "NORM-2026-1604569098147256870",
  "fonte": {
    "fonte_slug": "cofen_dou",
    "norma_origem": "BR_FED_COFEN_RES_2026_N_00801",
    "dispositivo_legal": "Art. 5º",
    "link_fonte": "https://www.in.gov.br/web/dou/-/resolucao-cofen-n-801/..."
  },
  "conteudo": {
    "texto_regra": "O enfermeiro pode prescrever medicamentos...",
    "idioma": "pt-BR",
    "charset": "UTF-8"
  },
  "identidade": {
    "sha256_texto": "sha256:abc123...",
    "sha256_original": "sha256:def456...",
    "hash_status": "CONFERIDO",
    "tamanho_bytes": 342
  },
  "politica": {
    "kernel_policy_id": "KERNEL-POLICY-001",
    "validators_passed": ["atomo_schema_validator", "norm_atom_id_validator", "texto_length_validator"],
    "fail_closed": true
  },
  "status": {
    "vigencia": "NÃO_VERIFICADO",
    "historico": [
      {"data": "2026-10-17T...", "status": "NÃO_VERIFICADO", "por": "kernel"}
    ]
  },
  "commit": {
    "sha": "abc123def456...",
    "author": "kernel-agent <kernel@indiciumfin.com>",
    "date": "2026-10-17T...",
    "wo_id": "WO-2026_10_17_0001",
    "reviewed_by": null
  },
  "restrictions": ["NO_DELETE", "NO_PUBLICATION", "RIGHTS_GATE_REQUIRED"]
}
```

### 7.2 Dicionário de Metadados

```json
// contracts/metadados_dicionario.json
{
  "schema": "CE-METADADOS-DICIONARIO-1.0.0",
  "campos": {
    "id_atomo": {
      "tipo": "string",
      "formato": "NORM-{ANO}-{INT12HEX}",
      "descricao": "ID canônico determinístico do átomo",
      "exemplo": "NORM-2026-1604569098147256870",
      "obrigatorio": true,
      "imutavel": true
    },
    "sha256_texto": {
      "tipo": "string",
      "formato": "sha256:{64hex}",
      "descricao": "SHA256 do texto normalizado (canonicalização)",
      "obrigatorio": true,
      "imutavel": true
    },
    "norma_origem": {
      "tipo": "string",
      "formato": "BR_FED_{ORGAO}_{TIPO}_{ANO}_N_{NUMERO}[_{SUB}]",
      "descricao": "Código normalizado da norma de origem",
      "exemplo": "BR_FED_COFEN_RES_2026_N_00801",
      "obrigatorio": true
    },
    "vigencia": {
      "tipo": "enum",
      "valores": ["NÃO_VERIFICADO", "VIGENTE", "ALTERADO", "REVOGADO", "SOB_DISCUSSAO"],
      "descricao": "Status de vigência do normativo",
      "obrigatorio": true,
      "transicoes_permitidas": {
        "NÃO_VERIFICADO": ["VIGENTE", "ALTERADO", "REVOGADO"],
        "VIGENTE": ["ALTERADO", "REVOGADO"],
        "ALTERADO": ["VIGENTE", "REVOGADO"],
        "REVOGADO": [],
        "SOB_DISCUSSAO": ["VIGENTE", "REVOGADO"]
      }
    }
  }
}
```

---

## 8. Plano de Implementação — Execução Total

### Fase A — Infraestrutura do Kernel (D1-D3)

| Dia | Tarefa | Entregável |
|---|---|---|
| D1 | Criar `packages/cli/kernel/` base | `kernel/__init__.py`, `kernel/core.py`, `kernel/policy_registry.py` |
| D1 | Criar `packages/cli/validators/base.py` | Interface `BaseValidator` + registry |
| D1 | Criar validadores P0 (atomo, sha256, norm_id, length) | 4 validadores com 50+ testes cada |
| D2 | Criar `contracts/{fonte}.json` para 20 fontes | 20 contratos de fonte |
| D2 | Criar políticas `KERNEL-POLICY-*` para 20 fontes | 20 políticas no registry |
| D2 | Criar `kernel/cli.py` — Typer CLI universal | CLI com 8 comandos |
| D3 | Criar workflows de update para fontes schedule | 5 workflows (CID-10, CID-11, MeSH, TACO, MedlinePlus) |
| D3 | Migrar `migrate_legado.py` para `kernel canonical` | CLI atualizada |
| D3 | Gate determinístico G1-G6 em `kernel gate` | Gate unificado |
| D3 | Testar kernel end-to-end com COFEN | 104.668 átomos processados |

### Fase B — Parsers por Fonte (D4-D10)

| Fonte | Parser | Tests | Política |
|---|---|---|---|
| CID-10 | `cid10.py` | 30 | KERNEL-POLICY-003 |
| CID-11 | `icd11.py` | 30 | KERNEL-POLICY-004 |
| MeSH | `mesh.py` | 30 | KERNEL-POLICY-005 |
| ANVISA Medicamentos | `anvisa_med.py` | 30 | KERNEL-POLICY-006 |
| Vacinas CDC | `vacinas.py` | 30 | KERNEL-POLICY-007 |
| FHIR Sinais Vitais | `fhir.py` | 30 | KERNEL-POLICY-008 |
| ANVISA Dispositivos | `anvisa_dev.py` | 30 | KERNEL-POLICY-009 |
| TACO Nutricional | `taco.py` | 30 | KERNEL-POLICY-010 |
| SINAN Epidemiologia | `sinan.py` | 30 | KERNEL-POLICY-011 |
| PNI Vacinal | `pni.py` | 30 | KERNEL-POLICY-012 |
| CATMAT Suprimentos | `catmat.py` | 30 | KERNEL-POLICY-013 |
| ESAVI Eventos | `esavi.py` | 30 | KERNEL-POLICY-014 |
| MedlinePlus | `medlineplus.py` | 30 | KERNEL-POLICY-015 |
| SIES OEBS | `sies.py` | 20 | KERNEL-POLICY-016 |
| Atlas Parts | `atlas.py` | 20 | KERNEL-POLICY-017 |
| CDSI Calendário | `cdsi.py` | 20 | KERNEL-POLICY-018 |

### Fase C — Homologação End-to-End (D11-D14)

| Dia | Tarefa | Entregável |
|---|---|---|
| D11 | WO-0090, WO-0091, WO-0087, WO-0088 | 4 lotes processados |
| D11 | Deduplicação cross-corpus SHA256 | 104.668 átomos deduplicados |
| D12 | migrate_legado → kernel canonical | 104.668 átomos canonical |
| D12 | Limpeza directorio legado | Diretório limpo |
| D13 | Revisão humana G6 (enfermeiro) | 10 átomos sampleados revisados |
| D13 | Atualizar DETERMINISTIC_RULES.md | Regras homologadas |
| D14 | PR cursor/atomizacao-full → main | PR com 1 reviewer |

### Fase D — Consolidação Main (D15+)

| Tarefa | Status |
|---|---|
| Branch protection na main | ⏳ |
| Supabase schema atualizado | ⏳ |
| SUPABASE_URL + ANON_KEY | ⏳ |
| All 18 parsers commitados | 🔲 |
| All 20 políticas homologadas | 🔲 |
| All workflows scheduleados | 🔲 |

---

## 9. Regra Final

> **Se não tem política no Kernel → o Kernel rejeita → exit 2.**
>
> Nada entra, nada sai, nada muda sem política registrada.
> A política é a lei do sistema.
