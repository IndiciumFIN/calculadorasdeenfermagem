# CE-BRANCH-QUARANTINE-20261115 — Bloqueio de branches candidatas à exclusão

**Estado:** política candidata versionada; execução na main e exigência do status check dependem de merge e configuração das regras do GitHub.  
**Âmbito:** IndiciumFIN/dev-chatgpt-workspace, IndiciumFIN/calculadorasdeenfermagem e backup privado (somente registro/retencão).  
**Fontes:** auditoria GitHub de 15/11/2026, comparação 'main...branch', inventário de PRs abertas e registro de aposentadoria existente `audit/branch-retirement/ncos-pr30-structural-overlay-20261113.v1.json`.

## Regra mandatória para ChatGPT, Grok, DeepSeek, Manus, Cursor, agentes e humanos

Antes de escolher **qualquer branch** como origem para editar, clonar como baseline, fazer merge, cherry-pick, publicar, executar workflow ou gerar artefatos:
1. Ler `registers/governance/branch-quarantine.v1.json` na **main atual** do repositório (não na branch candidata).
2. Comparar **repositório + nome completo** da branch. Para entradas `QUARANTINED_PENDING_DELETE` ou `BACKUP_RETAINED`, tratar como **NÃO UTILIZAR** nas finalidades de `prohibit`, independentemente do SHA, de passar testes ou de estar contida na main.
3. Utilizar `node scripts/verify-branch-quarantine.mjs --repo IndiciumFIN/<repo> --ref <branch> --purpose source` antes da seleção operacional; repetir na promoção/deploy com o propósito correspondente.
4. Se o manifesto estiver ausente, incompleto ou contraditório, ou se o gate não puder rodar: **HOLD_HUMAN**. Nunca interpretar ausência de branch como autorização para recriá-la.
5. Referências de evidência histórica, hashes e PRs antigas podem ser **lidas** sem checkout operacional, alteração ou publicação; o registro original permanece imutável.
6. Não criar novas branches com nomes quarentenados. Somente uma revisão formal versionada do manifesto com provas de segurança e autorização do proprietário pode mudar o estado.
7. `ahead_by=0` comprova apenas ausência de commits exclusivos no momento da consulta; **não** comprova ausência de consumidores externos nem autoriza exclusão.

## Classificação e risco

- **7 branches** de `dev-chatgpt-workspace` e **2** de `calculadorasdeenfermagem`: quarantena de uso operacional. Exclusão permanece pendente de varredura de referências (e checagem de SHA no instante da exclusão).
- **2 branches** do `calculadorasdeenfermagem-backup-20261031`: retenção de backup; **não excluir** sem política e ponto de restauração aprovados.
- `integration/structural-overlay-20261101`: evidência específica de **HOLD_REFERENCE_DEPENDENCIES** — há referências em scripts de auditoria, workflows e inventários históricos que precisam ser classificadas/migradas. A auditoria anterior não bastou para autorizar eliminação.
- Registros históricos como `registers/governance/main-migration-scope.v1.json` **não devem ser reescritos retroativamente**. Corrigir consumidores ativos, preservando os registros originais e seus SHAs.

## Controles operacionais

- **Preventivo para agentes:** instrução expressa neste documento e no arquivo de agentes do repositório; selecionar `main` ou branch candidata ainda não quarentenada após verificação.
- **Preventivo no CI:** `.github/workflows/branch-quarantine.yml` chama `scripts/verify-branch-quarantine.mjs --check-event` para bloquear PRs originadas ou destinadas a refs quarentenadas no próprio repositório; testes adversariais cobrem alterações no registro.
- **Antes de scripts locais e orquestradores:** executar a CLI de validação acima como primeira etapa. O resultado `PASS` significa apenas que a branch **não está nesta lista**, não GO clínico, funcional, jurídico ou de segurança.
- **Exigência para merge:** em GitHub Settings → Rules → Rulesets, adicionar o check **`branch-quarantine / authorize-ref`** como *required* para a `main`. Sem isso, um check vermelho pode não impedir todas as vias de promoção.
- **Vercel/infra:** configurar verificação equivalente em cada pipeline de preview e deploy; apenas a documentação/CI não bloqueia builds externos automaticamente.
- **Alcance:** não é possível tornar um Markdown ou um workflow isolado uma trava universal para todos os agentes e programas externos. Proteções devem ser habilitadas em cada integração; scripts que não consultam esta política ainda precisam ser adaptados.

## Desativação e exclusão de uma entrada

Requer: (1) inventário de referências executáveis e externas; (2) substituição por ref não quarentenada ou SHA imutável em usos históricos; (3) testes e revisão de conflitos; (4) SHA de destino revalidado e `ahead_by=0`; (5) backup/restauração provados quando aplicável; (6) autorização humana específica; (7) registro de execução. Até então: **HOLD_HUMAN**. Sem alterar dados do Supabase, sem migrations, sem merge automático ou deploy.

## Gate independente contra alterações maliciosas de PR

`.github/workflows/branch-quarantine-trusted.yml` usa `pull_request_target` e consulta **exclusivamente a `main` confiável**, sem executar nem conferir checkout do código de uma PR. O job exigível chama-se **`branch-quarantine / authorize-ref-trusted`**. O workflow `pull_request` anterior permanece como diagnóstico na PR, mas **não é suficiente como controle de acesso** porque uma PR pode alterar o próprio script.

**Ativação:** este workflow só começa a proteger novas PRs depois de estar integrado à `main`; exigir seu check em Rulesets/Branch Protection e proibir bypass de administradores. Até isso ocorrer, a proteção não está operacional. O GitHub não fornece garantia sobre orquestradores externos sem integração própria. Não habilitar pull_request_target com permissões de escrita nem executar código da PR.
