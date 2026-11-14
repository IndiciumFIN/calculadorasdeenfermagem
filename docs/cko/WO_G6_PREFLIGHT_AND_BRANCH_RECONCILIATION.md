# Pré-admissão técnica do Kernel e G6 — reconciliação de implementações legadas

**Data da revisão:** 14/11/2026. **Estado:** `DRAFT / HOLD_INDEPENDENT_REVIEW / HOLD_NORMATIVE / HOLD_RIGHTS`.

## Objetivo

Eliminar decisões que promovam Work Orders ou conteúdo clínico por **menção de texto**, campo de aprovação autodeclarado, presença de credencial ou CI verde. Manter o fluxo obrigatório `FIND → política → validador → tarefa → WO versionada → recibo Kernel → execução isolada → auditoria independente → promoção`.

Esta entrega é um **preflight somente leitura**. O Kernel atual não deve reinterpretar seu `HOLD` como `APPROVED`. O gate não acessa Drive/Supabase, não usa token de usuário, não envia dados, não grava WOs, não publica e **sempre devolve exit 2 para tentar executar uma WO**.

## Evidências originais pinadas e conflitos

| Branch | Arquivo histórico | Divergência encontrada | Regra de conciliação |
|---|---|---|---|
| `cursor/atomiza-o-arquivos-kernel-ebc1` (`f98902cb...`) | `packages/cli/kernel_work_order.py` | `_authorization_mentions` pesquisa ID da pasta em texto livre de qualquer WO; `_validator_names` obtém nomes por regex do arquivo, não por verificação funcional | Não importar como mecanismo de admissão; exigir referências tipadas e validação real |
| `cursor/arquivos-kernel-pol-ticas-8061` (`ce23049...`) | `packages/cli/kernel/work_orders.py` | `human_authorization_present` aceita `PREAUTHORIZED` + string de aprovador sem validar recibo independente/sha; `submit_drive_activities` chama `probe_drive_metadata_status` antes de decisão de autorização | Proibir sondagem de rede em preflight; nenhuma autodeclaração de aprovação concede privilégio |
| `fix/ce05-kernel-ci-security-20261017` (`e1c9ace...`) | `contracts/wo/WO-G0-CORRECTIVE-20261017.json` | WO original está em `DRAFT_NOT_ADMITTED`, refere 17 FINDs e critérios de aceite mencionam 11; não traz ligação estruturada pasta/atividade/política | Manter como candidato histórico, não preencher campos retroativamente nem supor admissão |
| `fix/canonical-structural-cli-registry-20261114` (`14fdc8a...`) | `packages/cli/kernel/core.py` | Implementa HOLD clínico e rejeição de validadores ausentes; ainda não possui serviço confiável de admissão/assinatura de WO/revisão humana | Acrescentar preflight separado, sem permitir override de `_release_on_hold` |

**Normas internas:** `docs/GOVERNANCE.md`, `docs/GATES.md`, `docs/DETERMINISTIC_RULES.md`; `migration/pilot-policies-20261017` e `fix/ce05-kernel-ci-security-20261017` são propostas expressamente não homologadas. Um `Reviewed-by:` no texto de commit **não** comprova identidade profissional nem verificação independente.

## Artefatos de código e teste

- `packages/cli/kernel/wo_preflight.py`: carrega o arquivo de raízes, política e WO com caminho seguro; vincula **Git blob SHA-1 real** (inclui NUL após cabeçalho Git) dos três documentos; exige pasta/atividade/política/tarefa/FINDs explícitos, sinaliza campos autoassinados, permanece HOLD por metadados apenas e falta de recibo externo.
- `tests/test_kernel_wo_g6_preflight.py`: 15 cenários sintéticos, inclusive as duas classes de bypass histórico, path traversal, symlink fora do repo, revisão autodeclarada, ausência de WO e hash Git.
- `scripts/cko_g6_preflight.py`: lê snapshot PMO M08/M09 e verifica unicidade + ligações `SOURCE → CONTENT`, `EVIDENCE_ATOM → CLAIM`, `CLAIM → CONTENT`, referência ao artigo, estados de HOLD; suporta múltiplas fontes normativas por mestre e **não** aprova vigência, direitos ou liberação clínica.
- `tests/test_cko_g6_preflight.py`: 13 cenários negativos de campo forjado, revisão autodeclarada, fonte órfã, claim órfão, duplicidade, conflito omitido e publicação indevida.
- `.github/workflows/cko-wo-g6-preflight.yml`: roda testes, lê **snapshot PMO pinado** no commit `d395f6e69e935570d5355ba930745bf8cd91f537`, lê **WO G0 histórica pinada** no commit `e1c9ace498b66ac831849ad1df51ee14e11e3efc`, confirma status HOLD, e armazena apenas relatórios resumidos no artifact privado do GitHub Actions.

### Semântica dos códigos de retorno

| Operação | Condição | Saída |
|---|---|---|
| Inspeção sintética | Todos os vínculos coerentes | `technically_complete=true` e `status=HOLD`; **exit 2** |
| WO real | Falta pasta/atividade/política/recibo independente | `status=HOLD`; **exit 2**; rede não acessada |
| Auditoria candidata PMO com `--diagnostic-only` | Grafo coerente e registros HOLD preservados | **exit 0 técnico exclusivamente para diagnóstico**; `clinical_release_gate_exit_code=2`; `can_publish=false` |
| Auditoria PMO sem `--diagnostic-only` | Qualquer conteúdo, mesmo estruturalmente coerente | **exit 2** |
| Falta fonte, JSON malformado, caminho inseguro ou referência órfã | Reprova a evidência | **exit 2** sem inferir dados faltantes |

## Segurança adicional comprovada após o primeiro preflight

- `packages/cli/kernel/core.py`: um `KERNEL-POLICY-001` ou qualquer política de fonte normativa real **não** pode obter `APPROVED` apenas desligando `requires_human_review`, `wo_required`, `sha256_required` e alterando `publication_allowed`/`rights_by_operation_approved` no mesmo JSON. Permanece `PENDING_HUMAN_REVIEW`.
- `packages/cli/kernel/policy_registry.py`: `SYNTHETIC_ONLY` é permitido somente em objeto de fixture criado em memória para testes; o registry recusa tal campo quando persistido em contratos do Git. Isto impede autodeclaração de escopo sintético por PR maliciosa.
- `packages/cli/kernel/wo_preflight.py`: detecta o conflito quantitativo real da WO G0 com **17 FINDs referenciados** contra critério de aceite **"All 11 FINDs closed"**; marca `WO_FIND_ACCEPTANCE_SCOPE_CONFLICT` e nunca escolhe um dos números por inferência.
- Testes de regressão dos escopos sintético/normativo e da discrepância de FINDs rodados no Actions, junto com os 15 testes WO e 13 testes G6. O sucesso técnico **não** altera o estado clínico HOLD.

## Limites e próximos gates obrigatórios

1. **Autoridade de identidade:** mapear revisor humano nominal por credencial verificada fora do commit (competência, independência, vigência profissional), e aprovações de GitHub obtidas da API com HEAD SHA do PR e permissões efetivas. O preflight **não** pode criar essa prova.
2. **Vínculo imutável:** recibo assinado por autoridade externa habilitada deve referenciar o Git blob SHA da WO, source version, evidence span hashes, claim IDs, tipos de uso/licença, escopo exato e validade; em caso de mudança após assinatura, voltar a HOLD.
3. **Fonte normativa oficial:** confirmar atos e alterações em repositório oficial/diário, vigência por artigo, direitos de reutilização e pertinência clínica; `M03_RECOVERED_SOURCE_TEXT` não prova sozinho edição vigente nem fidelidade à publicação oficial.
4. **Dupla revisão:** auditor técnico não executa autoaprovação; revisão clínica e regulatória independente; HIT de privacidade antes de qualquer dado pessoal. Cada um dos 46 claims requer decisão rastreável, não aprovação do lote pelo número de itens.
5. **G6 no branch rules:** verificar que as proteções reais impedem merge sem status checks e aprovação qualificada; a API de configuração da `main` respondeu 403 na auditoria #51 e não demonstra proteção instalada.
6. **Sem adoção automática das branches históricas:** a [WO #55](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/55) mantém 33 PRs Cursor sob reconciliação e revisão de efeitos colaterais, sem excluir ou mesclar.

## Proibições deliberadas

Não copiar de `cursor/arquivos-kernel-pol-ticas-8061` o probe que realiza requisição antes da autorização; não usar apenas nomes regex de validadores; não inferir aprovação por `PREAUTHORIZED`, `approved_by` ou texto `Reviewed-by`; não substituir o SHA real do blob por hash de serialização/objeto normalizado; não tomar PASS de testes ou metamodelos como comprovação clínica.

**Parecer:** `GO_TECHNICAL_CANDIDATE_TESTS / HOLD_WO_ADMISSION / HOLD_G6_HUMAN / HOLD_CLINICAL / HOLD_EXTERNAL_SOURCE_VIGENCY`.
