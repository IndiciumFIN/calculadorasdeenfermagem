# Matriz de Controles Chave (Key Controls)

| ID | Tarefa | Risco | Controle implementado | Onde |
|----|--------|-------|-----------------------|------|
| KC-01 | Ingestão | Layout muda e extrai lixo | Máscara + seletores amplos + hash | `cli/utils.py` |
| KC-02 | Atomização | Alucinação de prazos/valores | Extração de números + auditoria de omissão | `cli/auditor.py` |
| KC-03 | Validação | Payload quebrado ou opinativo | Invariantes Pydantic | `schemas/invariantes.py` |
| KC-04 | Publicação | Dado sem fonte | Fail-fast se status=Vigente e sem link | invariantes |
| KC-05 | Documentação | Dicionário desatualizado | Geração a partir do schema (próximo passo) | CLI docs_generate |

**Regra de ouro**: se qualquer controle falhar, o processo aborta (exit code 2).
