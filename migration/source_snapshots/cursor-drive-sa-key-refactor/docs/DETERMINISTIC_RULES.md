# Regras Determinísticas — Calculadoras de Enfermagem
**Versão:** 1.0.0
**Data:** 2026-10-17
**Validade:** todas as branches e CI/CD

---

## Regra 0 — Imutabilidade do SHA256

> **SHA256 é a identidade do átomo. Nunca é alterado pós-commit.**

Um SHA256 registrado no MANIFESTO é a prova de que o átomo está intacto. Se o texto muda, o SHA256 muda → é um átomo diferente.

**Verificação:**
```bash
sha256sum data/canonical/atoms/*.json
# Deve coincidir com o SHA256 registrado no MANIFESTO do domínio
```

---

## Regra 1 — Átomo Nasce "Não Verificado"

> **Nenhum átomo nasce "Vigente" ou "Ativo".**

Obrigação de `GOV-004`: a vigência de um normativo vem do Diário Oficial, não da planilha do Drive. Como a planilha é uma cópia parcial (pode ter erros de transcrição), o átomo só recebe vigência após:
1. Revisão humana (G6)
2. Confirmação de que o texto coincide com o DOU
3. Assinatura de um enfermeiro revisor

---

## Regra 2 — Quarentena Sem Truncamento

> **Texto < 10 chars ou > 800 chars vai para quarentena integral — sem corte.**

O límite de 800 caracteres no contrato `AtomoBlindado` existe porque átomos maiores fragmentam o raciocínio clínico. Mas o texto integral é **sempre** preservado na Quarentena para auditoria.

**Campos da Quarentena:**
```
texto_regra_inteiro    — o texto como veio da fonte
motivo                 — texto_curto | acima_contrato | conflito_duplicata | termo_opinativo
fonte                  — arquivo de origem
sha256_original        — SHA256 do texto integral
sha256_transformado    — SHA256 após normalização
```

---

## Regra 3 — Fail-Closed no Pipeline

> **Qualquer anomalia para o pipeline em dúvida deve falhar — não prosseguir.**

Testes fail-closed:
- Metadados Drive ausentes → `ValueError` + exit 2
- PáginaToken repetido → `ValueError` + exit 2
- Pasta > 100.000 itens → `ValueError` + exit 2
- Acesso sem credencial → exit 2 (não vazio)
- WO sem `sha256_fonte` → exit 2
- Corpus vazio após migrate → exit 2

---

## Regra 4 — ID Canônico Determinístico

> **O ID do átomo é gerado pelo algoritmo — não há escolha humana.**

```
ID = f"NORM-{ano}-{int(sha256(legacy_id)[:12], 16)}"
```

Exemplo: `legacy_id = "BR_FED_COFEN_RES_2026_N_00801_ART_001"`
```
sha256("BR_FED_COFEN_RES_2026_N_00801_ART_001")[:12] = "3a4b5c6d7e8f"
int("3a4b5c6d7e8f", 16) = 1604569098147256870
ID = "NORM-2026-1604569098147256870"
```

**Propriedades:**
- O mesmo `legacy_id` gera o mesmo ID em qualquer máquina
- ID diferente = átomo diferente (sem ambiguidade)
- Não há colisão known no corpus de 104.668 átomos

---

## Regra 5 — Nome de Arquivo = ID do Átomo

> **Arquivo no disco = `{id_atomo}.json`**

```python
id_atomo = "NORM-2026-1604569098147256870"
path = f"data/canonical/atoms/{id_atomo}.json"
```

Isso permite:
- Busca direta por ID sem index
- Verificação de duplicação por nome de arquivo
- Deduplicação determinística: se o arquivo existe, o átomo já está

---

## Regra 6 — Commit como Evidência

> **Cada commit no corpus canônico registra: fonte, data, autor, SHA256.**

```json
{
  "id_atomo": "NORM-2026-...",
  "sha256_texto": "abc123...",
  "commit_sha": "def456...",
  "commit_author": "agent@indiciumfin.com",
  "commit_date": "2026-10-17T...",
  "fonte_tipo": "NORMATIVE_ATOMS_COFEN_LOTE2",
  "origem": "data/legado/fontes/NORMATIVE_ATOMS_COFEN_LOTE2_V1.xlsx"
}
```

---

## Regra 7 — Quarentena É Auditável

> **Tudo que entra na Quarentena tem registro imutável.**

```bash
# Cada rejeição gera uma linha no .jsonl
jq '.motivo' data/quarentena/*.jsonl | sort | uniq -c | sort -rn
# texto_curto      5718
# acima_contrato   1044
# conflito_duplicata 752
# termo_opinativo   165
```

Revisões de Quarentena geram novos commits — nunca alteram o histórico de rejeições.

---

## Regra 8 — WO como Autorização Formal

> **Nada é baixado, atomizado ou migrado sem WO formalizada.**

```json
// data/legado/autorizacao_WO-0090.json
{
  "id": "WO-2026_10_15_0090",
  "tarefa": "obter",
  "lote": "cofen_dec_abaixo_50",
  "entradas": 12,
  "estado": "PREAUTHORIZED",
  "autorizado_por": "agent@indiciumfin.com",
  "data": "2026-10-15T..."
}
```

Uma WO é um arquivo versionado no Git — é a trilha de auditoria que diz **quem pediu, o quê, quando, para qual lote**.

---

## Regra 9 — Estorno de WO Bloqueado

> **WO com estado BLOQUEADO registra o motivo técnico exato.**

```json
// data/legado/autorizacao_WO-0087.json
{
  "id": "WO-2026_10_15_0087",
  "tarefa": "obter",
  "lote": "nativos_google",
  "estado": "BLOQUEADO",
  "motivo": "Download público da planilha native 1vi129pgX... respondeu 500 após retries.",
  "tentativas": 3,
  "ultimo_http_code": 500,
  "acao_necessaria": "Usar GDRIVE_SA_KEY para download autenticado (WIP)"
}
```

WO BLOQUEADA nunca some — ela fica no tracker até ser resolvida.

---

## Resumo Rápido

| Regra | Nome | Implicação |
|---|---|---|
| R0 | SHA256 = identidade | Texto muda → SHA256 muda → átomo diferente |
| R1 | Não verificado por padrão | Vigência exige revisão humana + DOU |
| R2 | Quarentena sem truncamento | Texto integral preservado para auditoria |
| R3 | Fail-closed | Anomalia = exit 2, não prosseguir |
| R4 | ID determinístico | `NORM-{ano}-{int(sha256(legacy_id)[:12], 16)}` |
| R5 | Arquivo = ID | Sem index, busca direta por nome |
| R6 | Commit como evidência | sha256, autor, data, fonte no registro |
| R7 | Quarentena auditável | JSONL append-only, nunca alterado |
| R8 | WO formalizada | Nada sem autorização versionada |
| R9 | Bloqueado documentado | Motivo técnico exato no registro |
