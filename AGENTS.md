# AGENTS.md — Contrato de seleção de branches (CE)

**REGRA PRIORITÁRIA DE GOVERNANÇA:** ler `docs/governance/BRANCH_QUARANTINE_POLICY.md` e `registers/governance/branch-quarantine.v1.json` na `main` antes de usar qualquer branch como source, base, desenvolvimento, merge, workflow ou deploy. Ramo na quarentena = **HOLD_HUMAN**; jamais contornar por cherry-pick, ref remoto ou restauração do nome. Executar `node scripts/verify-branch-quarantine.mjs --repo IndiciumFIN/calculadorasdeenfermagem --ref "<branch>" --purpose source` para a seleção. Não tratar `PASS` como aprovação clínica/Kernel.

Preservar evidências e snapshots históricos somente leitura. Não apagar branches, refazer migrations, promover produção, enfraquecer CI/RLS ou ignorar gates de segurança/COFEN sem procedimento formal e autorização de escopo. Se o manifesto ou gate estiver indisponível, falhar fechado: `HOLD_HUMAN`.
