# CE — ferramentas públicas e governança no painel (v0.1.0)

Pacote incremental para adicionar ao projeto **Next.js** em uma **branch isolada**. Não altera a `main`, o site estático nem o banco de produção.

- Fonte: estudos v1.0–v1.4 do Calculadoras de Enfermagem.
- Registry de trabalho e controle de publicação imutável no backend (SQL **candidato**, não aplicado).
- 24 demandas pesquisa originárias, em HOLD. Registro de reconciliação de 68 capacidades prévias e 36 candidatas UX.
- APIs públicas apenas leem releases autorizadas.
- Painel administrativo cria/edita candidatos e envia para revisão; não publica.
- As tools publicadas, quando existir concessão Kernel, são renderizadas pelo componente compartilhado.
- Gates e artefatos de integridade em `scripts/verify_governed_tools.py`.

**Governança:** é imprescindível obter uma Work Order válida no Kernel antes da migração ou promoção. Consulte `docs/ecossistema/IMPLEMENTACAO_BACKEND_GOVERNADO_v0.1.0.md`.
