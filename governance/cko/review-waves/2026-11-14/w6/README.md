# W6 — Centro Cirúrgico e SRPA (CKO/NCOS)

**DRAFT_EDITORIAL / HOLD_SOURCE / HOLD_RIGHTS / HOLD_HUMAN / NO_GO**

Entrega de conteúdo educacional efetivo para estudo sobre Centro Cirúrgico e SRPA, sem confundir ambos com o módulo CME W5 ou com a trilha curricular de Cardiologia. Contém duas aulas independentes, uma aula de continuidade e sete casos fictícios, mais 16 questões comentadas e 16 flashcards para candidatos à avaliação formativa.

## Origem, sem perda
- **5/5 arquivos Drive originais íntegros** em `originais/`; hashes/SHA-256 em `dados/LEGACY_ASSET_RECOVERY.json`.
- Normas e documentos oficiais em `normas/PRIMARY_SOURCES_LEDGER.csv` (sem texto integral protegido e **fragment hashes pendentes**).
- `dados/REUSE_GRAPH_EDGES_W6.jsonl`: links candidatos com `semantics_approved=false`, `rights_verified=false` e `publication_allowed=false`.
- `qa/FINDINGS_W6.csv`: achados específicos, sem encerrar `HOLD` por QA estrutural.

## Diagnósticos importantes
Aldrete HTML em `th-TH` com trechos pt-BR e afirmação de alta que exige validação; ELPO recuperada somente como fragmento SEO; SAEP em es-ES; checklist e simulado HTML com lang nl-NL. As 30 questões **legadas** do simulado não foram copiadas para o banco editorial W6; as 16 questões W6 são novas e precisam de revisão de referências.

## Fronteira operacional
Sem dose, manobra, interpretação de escala, corte de alta, indicação clínica, checklist operacional ou aplicação de POP. `CONTEXTUALIZES` ≠ `EQUIVALENT_TO`. Não criar nova biblioteca, UC, módulo curricular ou tabela; não publicar ou enviar ao repositório público em lugar do privado.

## QA
Execute `python tools/validate_w6.py`. O relatório local registra apenas teste estrutural e de limites de segurança. Para governança, ler `governanca/RECONCILIACAO_W6.md`.
