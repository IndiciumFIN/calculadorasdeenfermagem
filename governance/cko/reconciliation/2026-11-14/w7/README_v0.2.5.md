# CKO W7 v0.2.5 — prova de bytes sem substituir fonte primária

**HOLD_PRIMARY_SOURCE_BYTES / HOLD_RIGHTS / HOLD_LEGAL_CURRENTNESS / HOLD_CLINICAL / NO_GO**

## Resultado material
Em consulta aos dois Drives conectados, os dois IDs de PDF de origem para a Resolução COFEN 736/2024 registrados no Supabase (`calculadoras_de_enfermagem.document_atomization`) retornaram 404 em 4 tentativas diretas. Preservamos nomes e hashes esperados, mas não expomos IDs privados nem concluímos que os arquivos foram apagados.

Foi recuperado um documento diferente: `RES_2024_N_00736_DOSSIE_V0.pdf` (2 páginas, 473.460 bytes, hash SHA-256 `f444472c9df74f87d9d9df0dad44368fe63c5e0475411cb6ec7d5f3cc7cadc59`). O texto do próprio dossiê informa que a conferência do texto normativo integral, alterações posteriores e direitos permanece pendente e que o PDF oficial não foi baixado para aquele lote. Esse hash corresponde apenas ao **dossiê derivado**, nunca à publicação oficial.

Inspecionadas na web as páginas oficiais COFEN 736/2024 e COFEN 754/2024 (DOU), e a primeira página da cópia da RDC Anvisa 15/2012 no Ministério da Saúde. A transferência binária desta última falhou por resolução DNS no ambiente local. As URLs são localizadores oficiais consultados, não provas de bytes preservados.

## Artefatos deste commit
- `audit/COFEN736_DRIVE_DOSSIER_RECEIPT_v0.2.5.json`: recibo byte-a-byte, sem PDF.
- `audit/COFEN736_PRIMARY_RECOVERY_LOOKUP_v0.2.5.json`: duas referências primárias do Supabase e buscas 404 em ambas as contas, sem IDs privados.
- `audit/OFFICIAL_SOURCE_BYTE_AVAILABILITY_v0.2.5.jsonl`: três fontes oficiais e um dossiê secundário classificados.
- `audit/FINDINGS_DELTA_v0.2.5.json`: dois novos achados e atualização de W7-008.
- `audit/QA_BYTE_VERIFICATION_v0.2.5.json`: escopo do teste, oito testes locais e comprovação de hash secundário.
- `tools/verify_normative_pdf_bytes_v0.2.5.py`: verificador offline fail-closed; saída só metadados, não copia PDF nem autoriza publicação.
- `tests/test_verify_normative_pdf_bytes_v025.py`: oito testes executáveis por `python -m unittest discover`.

Uso no Codespaces: execute `python -m unittest discover -s governance/cko/reconciliation/2026-11-14/w7/tests -p 'test*.py' -v`. Para verificar um documento recuperado autorizado:
`python governance/cko/reconciliation/2026-11-14/w7/tools/verify_normative_pdf_bytes_v0.2.5.py --input /caminho/arquivo.pdf --expected-sha256 HASH64 --kind OFFICIAL_PRIMARY_CANDIDATE`

Um hash correto prova somente igualdade de bytes com o digest esperado. A admissibilidade documental, vigência normativa, direitos, semântica e aprovação clínica permanecem independentes e **não são automatizadas**.

**Sem merge, sem deploy, sem alteração ao Supabase nem anexos integrais de terceiros na branch pública.**
