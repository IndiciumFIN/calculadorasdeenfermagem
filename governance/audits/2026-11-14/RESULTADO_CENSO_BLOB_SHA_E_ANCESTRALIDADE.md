# Censo Git completo por blob, árvore e ancestralidade — 14/11/2026

**Estado:** `READ_ONLY_VERIFIED / NO_DELETE / NO_MERGE / CLINICAL_HOLD`

**Evidência de execução:** [GitHub Actions #43589267861](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43589267861), código do censo `scripts/cko_branch_census.py`, testes negativos `tests/test_cko_branch_census.py`, workflow `.github/workflows/cko-branches-cross-audit.yml`.

O job executou 10 testes sintéticos adversariais (PASS) e percorreu todas as branches presentes no repositório privado, usando `GET /git/trees/{sha}?recursive=1` com rejeição de truncamento, `compare/main...head` para ancestralidade, mais PRs paginadas. A saída `census.json` foi salva como artefato privado do Actions, vinculado ao commit `310fcc37838091a1e32d92cdc8de951701ee38db`. Sem leitura do conteúdo de blobs (apenas caminho, identidade SHA e ação).

## Totais verificáveis no snapshot

| Métrica | Contagem | Interpretação |
|---|---:|---|
| Branches verificadas | **57** | Inclui as branches de auditoria e CI criadas em 14/11 |
| PRs abertas | **43** | 33 com branch `cursor/*` |
| Branches cursor/* | **36** | Com potencial de sobreposição de WO/Drive e Kernel |
| Branches com árvore distinta de main | **55** | Não diz quantas são homologadas; duas árvores coincidem com `main` |
| Branches com ancestralidade divergente de main | **7** | Exige estratégia de rebase/cherry-pick revisada |
| Grupos de árvores Git idênticas | **1** | `main` e `staging/cko-migracao-2026-10-23` |
| Grupos de deltas exatos contra main | **1** | O mesmo par sem alteração em relação à main |
| Pares cursor/* com alteração de caminhos sobrepostos relevante | **25** | Não são 25 duplicatas; muitos pares possuem blobs diferentes |
| Branches com nomes de caminhos potencialmente sensíveis | **4** | Indício por **nome** de arquivo; não demonstra vazamento de segredo |

### Única equivalência de árvore total

`main` e `staging/cko-migracao-2026-10-23` têm conteúdo de árvore Git idêntico. O censo comprova **identidade de conteúdo**, não ausência de dependência histórica, PR, TAG, branch protection, automação ou referência de PMO. **Classificação:** `CANDIDATE_ADMIN_CLEANUP / HOLD_DELETE_APPROVAL`. Não excluir sem aprovação e backup.

### Maior sobreposição nas branches históricas

`cursor/drive-sa-key-refactor` × `cursor/fix-governance-gaps-ec54`:
- **9.063 caminhos alterados em comum** em relação à main; **9.059** têm a mesma ação/hash.
- **4 caminhos têm conteúdo divergente**:
  - `.github/workflows/drive-recursive-collect.yml`
  - `.github/workflows/gate.yml`
  - `evidence/CE-WO-20261017-F00-07/raci.json`
  - `packages/cli/requirements.txt`
- Sobreposição Jaccard dos caminhos: **0,9966**. **Classificação:** `OVERLAP_NEAR_IDENTICAL_BUT_4_CONTENT_CONFLICTS / HOLD_MERGE`.
- Um merge direto é inadequado sem resolver o gate, RACI e dependências; as branches não são duplicatas exatas.

`cursor/wf-gdrive-sakey` × `cursor/wf-v3`:
- **113 caminhos idênticos em ação/hash** no conjunto comum e **nenhum blob conflitante nos caminhos compartilhados**.
- O delta da branch `cursor/wf-v3` é subconjunto próprio do delta `cursor/wf-gdrive-sakey` (não igualdade de árvores completas).
- **Classificação:** `SUBSET_DELTA_CANDIDATE / HOLD_HISTORICAL_REFS`; excluir somente após verificar vínculos e workflow externo.

`cursor/arquivos-kernel-pol-ticas-7f24` × `cursor/arquivos-kernel-pol-ticas-d7f8`:
- **21 caminhos alterados em comum**, **16 iguais**, **5 conflitantes** (WO, decisão do Kernel e testes).
- Sobreposição de caminhos **100%**, mas os conteúdos são diferentes; não é caso de deduplicação simples.
- **Classificação:** `SAME_PATHSET_DIFFERENT_BYTES / REVIEW_KERNEL_WO_CONTRACT`.

`cursor/arquivos-kernel-pol-ticas-6bf4` × `cursor/arquivos-kernel-pol-ticas-c8ed`:
- 10 caminhos em comum, 6 iguais e 4 divergentes (autorizações de WO e evidências de bloqueio).
- **Classificação:** `REVIEW_AUTHORIZATION_AND_EVIDENCE_DIFF`.

### Branches realmente divergentes de main (ancestralidade GitHub)

| Branch | Ahead | Behind |
|---|---:|---:|
| `cursor/drive-sa-key-refactor` | 123 | 9 |
| `cursor/fix-governance-gaps-ec54` | 127 | 9 |
| `cursor/wf-gdrive-sakey` | 9 | 9 |
| `integration/canonical-main-20261017` | 8 | 6 |
| `migration/candidate-f08-20261017` | 10 | 4 |
| `migration/full-directory-20261017` | 2 | 4 |
| `staging/wo-kernel-normativos-cli-20261016` | 1 | 9 |

As divergências são propriedades de histórico Git, não prova de conflito funcional em cada arquivo. Outros caminhos podem afetar as mesmas interfaces e contratos mesmo sem divergência de ancestralidade.

## Controle de segurança e procedência

O detector de nomes de arquivos sinalizou quatro branches com caminhos potencialmente sensíveis: `cursor/drive-sa-key-refactor`, `cursor/fix-governance-gaps-ec54`, `migration/candidate-f08-20261017` e `migration/full-directory-20261017`. **Não houve inspeção do conteúdo de segredos; `.env.example` ou nomes informativos podem gerar falso positivo.** A triagem de segredos, licenças e LGPD é etapa separada e obrigatória antes de transferência, deleção ou publicação.

O corpus histórico grande inclui arquivos não cobertos pelas respostas REST de comparação que limitam a lista de arquivos modificados. O presente censo usou árvores completas não truncadas e identidade de **Git blob** para o cálculo dos deltas. **Não** realizou validação normativa, clínica, editorial ou de direitos de cada blob.

## Disposição e sequência para as 33 PRs Cursor

1. Congelar o snapshot `census.json` e os SHAs por PR/branch; registrar o artefato em PMO como **evidência de comparação**, não autorização.
2. Identificar famílias de contratos e algoritmos (WO/Drive, segurança Kernel, validações, fontes normativas). Não classificar como duplicado apenas pelo prefixo `cursor/` ou título semelhante.
3. Para os 25 pares sobrepostos, usar o relatório completo: caminhos conflitantes + blob SHA; reconciliar contratos e testes negativos sobre versão candidata única, por ordem de risco.
4. Revisar por fonte original eventuais scripts de Drive e tokens: `READ_ONLY` quando autorização ausente, `HOLD_SOURCE` se falta documento, `HOLD_HUMAN` quando falta auditor independente.
5. A única branch com árvore idêntica à main pode ser indicada para **avaliação de exclusão**, não excluir sem conferir referências ativas e autorização expressa; conservar evidência.
6. Implementar CI e G6 sem `|| echo`, e exigências de revisão humana/WO por SHA antes de qualquer integração.

## Conclusão operacional

**Censo completo da estrutura Git PASS, promoção NÃO autorizada.** São 57 branches e 43 PRs — e somente uma duplicação exata de árvore. Existem 25 pares Cursor com sobreposição relevante e diferenças em diferentes graus. O trabalho pendente é uma **reconciliação semântica e técnica**, não um simples merge em lote. Preservar `main`, o PMO, hashes, revisão clínica e direitos até decisão independente.
