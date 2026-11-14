# W7 v0.2.2 — localização de 17 atomizações PDF (HOLD)
**RECOVERY_TRIAGE_COMPLETE / ARTIFACT_BYTES_MISSING / HOLD_RIGHTS / NO_GO**

Consultada em modo somente leitura a relação `calculadoras_de_enfermagem.document_atomization` para o release `CKO-GROK-20261010-V1`: 17 registros, 25.508 átomos textuais e 887 referências visuais **reportados no banco**. Os 17 registros marcam `LOCAL_ARTIFACT_NOT_DURABLE`.

Foram feitas 17 consultas de **nome exato** em cada um dos **dois Google Drives conectados**. Resultado: 0 correspondências por título exato, sem erros de consulta. Isso **não comprova perda global**: os arquivos podem estar em ZIPs, backups ou localização fora dos Drives pesquisados.

## Artefatos novos
- `audit/PDF_JSONL_RECOVERY_INVENTORY_v0.2.2.jsonl`: 17 nomes esperados, hashes e contagens originais, sem IDs de arquivos privados.
- `audit/PDF_JSONL_RECOVERY_SUMMARY_v0.2.2.json`: evidência de busca e limites do resultado.
- `audit/QA_PDF_JSONL_RECOVERY_v0.2.2.json`: invariantes de 7 verificações.
- `tools/verify_pdf_jsonl_recovery_v0.2.2.py`: verificador local read-only. Exige bytes exatos e JSONL íntegro, retorna erro quando há arquivo ausente ou divergente.
- `audit/FINDING_STATUS_DELTA_v0.2.2.json`: W7-003 e WO-006 permanecem HOLD com busca realizada.

## Recuperação segura
Guardar qualquer JSONL localizado em repositório ou armazenamento autorizado, conferir SHA-256 com o manifesto, validar JSONL; conferir direitos de uso por operação. Somente depois registrar localização durável/imutável, com aprovação apropriada. Não gerar novos arquivos e chamá-los de originais; não copiar textos protegidos para esta branch pública.

**Sem atualização no Supabase, sem merge, sem mudança no histórico v0.2.0/v0.2.1 e sem aprovação clínica.**
