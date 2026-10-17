# Nomenclatura Padrão — Calculadoras de Enfermagem

## Princípio

Tudo no repositório segue uma convenção de nomes única. Inconsistências = fail-closed.

---

## Diretórios

| Diretório | Nome oficial | Regra |
|---|---|---|
| `contracts/` | Contratos | Schemas, políticas, fontes |
| `contracts/fontes/` | Contratos de fonte | Um arquivo por fonte oficial (slug `.json`) |
| `contracts/policies/` | Políticas do Kernel | Uma política por `.json` (ID do Kernel) |
| `packages/cli/` | CLI canônica | Comandos `packages/cli/main.py` |
| `packages/cli/kernel/` | Módulo Kernel | Executor de políticas |
| `packages/cli/validators/` | Validadores | Um validador por `.py` (snake_case) |
| `packages/schemas/` | Schemas Pydantic | Modelos de dados autoritativos |
| `data/canonical/` | Átomos canônicos | Saída validada do Kernel |
| `data/quarentena/` | Rejeitados | Átomos que falharam validação |

---

## Arquivos de Fonte (contracts/fontes/)

Formato: `{slug}.json`

| Fonte | Slug | Política |
|---|---|---|
| Normativo COFEN (DOU) | `cofen_dou` | KERNEL-POLICY-001 |
| Normativo ANVISA (DOU) | `anvisa_dou` | KERNEL-POLICY-002 |
| CID-10 (DATASUS) | `cid10` | KERNEL-POLICY-003 |
| CID-11 (OMS) | `cid11` | KERNEL-POLICY-004 |
| MeSH (NLM) | `mesh` | KERNEL-POLICY-005 |
| Medicamentos ANVISA | `anvisa_med` | KERNEL-POLICY-006 |
| Vacinas CDC CVX | `vacinas_cdc` | KERNEL-POLICY-007 |
| Sinais Vitais FHIR | `fhir_vitais` | KERNEL-POLICY-008 |
| Dispositivos ANVISA | `anvisa_dev` | KERNEL-POLICY-009 |
| TACO Nutricional | `taco` | KERNEL-POLICY-010 |
| SINAN Epidemiologia | `sinan` | KERNEL-POLICY-011 |
| PNI Vacinal | `pni` | KERNEL-POLICY-012 |
| CATMAT Suprimentos | `catmat` | KERNEL-POLICY-013 |
| ESAVI Eventos Adversos | `esavi` | KERNEL-POLICY-014 |
| MedlinePlus | `medlineplus` | KERNEL-POLICY-015 |
| SIES Insumos | `sies` | KERNEL-POLICY-016 |
| Atlas BodyParts3D | `atlas` | KERNEL-POLICY-017 |
| CDSI Calendário | `cdsi` | KERNEL-POLICY-018 |
| Portarias MS | `ms_portarias` | KERNEL-POLICY-019 |
| Leis Federais | `lei_federal` | KERNEL-POLICY-020 |

---

## Validadores (packages/cli/validators/)

Um módulo por validador. Nome do arquivo = nome do validador (snake_case).

| Validador | Arquivo | Testes |
|---|---|---|
| `sha256_validator` | `sha256_validator.py` | 11 |
| `norm_atom_id_validator` | `sha256_validator.py` | 11 |
| `texto_length_validator` | `sha256_validator.py` | 11 |
| `url_validator` | `sha256_validator.py` | 11 |
| `atomo_schema_validator` | `sha256_validator.py` | 11 |
| `cid10_validator` | `cid10_validator.py` | 11 (stub) |
| `cid11_validator` | `cid11_validator.py` | 11 (stub) |
| `mesh_validator` | `mesh_validator.py` | 11 (stub) |
| `cvx_validator` | `cvx_validator.py` | 11 (stub) |
| `schema_validator` | `schema_validator.py` | 11 (stub) |
| `loinc_validator` | `loinc_validator.py` | 11 (stub) |
| `ncm_validator` | `ncm_validator.py` | 11 (stub) |
| `catmat_validator` | `catmat_validator.py` | 11 (stub) |
| `human_review_validator` | `human_review_validator.py` | 11 (stub) |

---

## Schemas (packages/schemas/)

| Schema | Arquivo | Versão | Uso |
|---|---|---|---|
| `AtomoBlindado` | `invariantes.py` | 1.2.0 | Schema autoritativo do átomo |
| `AtomoNormativo` | `atomo.py` | — | Alias para `AtomoBlindado` |
| `EscalaClinica` | `escala.py` | — | Escala clínica |
| `ParametroEscala` | `escala.py` | — | Parâmetro de escala |

---

## Políticas (contracts/policies/)

Formato: `KERNEL-POLICY-{NNN}.json`

O `source_contract` de cada política aponta para `contracts/fontes/{slug}.json`.

---

## CLI (packages/cli/main.py)

```
python -m packages.cli.main ingest   --source <url> [--output file.json]
python -m packages.cli.main process  --input raw.json [--output atomos.json]
python -m packages.cli.main validate --input atomos.json [--strict]
python -m packages.cli.main kernel gate        KERNEL-POLICY-001
python -m packages.cli.main kernel validate   --policy KERNEL-POLICY-001 --input atomos.json
python -m packages.cli.main kernel list-policies
python -m packages.cli.main kernel test-validators
```

---

## Histórico de Correções

| Data | Correção |
|---|---|
| 2026-10-17 | `contracts/fonts/` → `contracts/fontes/` (criado novo) |
| 2026-10-17 | `source_contract` em 20 políticas corrigido para `contracts/fontes/{slug}.json` |
| 2026-10-17 | 9 validadores stubs criados (cid10, cid11, mesh, cvx, schema, loinc, ncm, catmat, human_review) |
| 2026-10-17 | `AtomoBlindado` consolidado em `packages/schemas/invariantes.py` (Pydantic v2) |
| 2026-10-17 | `pipeline.py` atualizado com etapa KERNEL_GATE |
| 2026-10-17 | `main.py` integrado com subcommand `kernel` |
| 2026-10-17 | `requirements.txt` atualizado com `google-auth>=2.30.0,<3` |
