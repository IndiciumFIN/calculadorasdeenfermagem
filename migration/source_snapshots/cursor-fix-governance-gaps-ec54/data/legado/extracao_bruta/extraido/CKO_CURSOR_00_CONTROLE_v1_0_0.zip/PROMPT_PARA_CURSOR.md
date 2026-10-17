# Instrução para o agente Cursor — análise controlada

Trabalhe exclusivamente em ambiente local e em leitura. Antes de analisar: leia `README_CURSOR.md` e `INVENTARIO_E_QA.json`; verifique SHA e intervalos com `fragmentar.py`.

Para cada parte:
- Identifique `source_sha256`, `source_drive_id`, intervalo de páginas e checksum dos fragmentos.
- Leia `.pages.jsonl` como guia; confira a fonte no PDF visual quando houver tabela, figura, cabeçalho, notas ou ambiguidades.
- Identifique requisitos candidatos, recomendações, critérios clínicos, sujeitos, condições, ressalvas e referências. NÃO converta automaticamente conteúdos clínicos em atos normativos.
- Relate cada problema por `FIND_CANDIDATE` com fonte exata (documento + página original), evidência textual sucinta, política aplicável e nível de confiança. Não declare FIND registrado no sistema.
- Produza apenas proposta/candidato de JSON ou relatório de revisão no espaço de trabalho isolado.
- NUNCA execute comandos de escrita no repositório, Drive, banco, Supabase, APIs, Registry, release ou publicação. Se uma ação depender de escrita, solicite WO validada e emissão pelo Kernel.
- Não use serviço externo para arquivos não autorizados por licença. Não use conteúdo parcial para diagnósticos clínicos.
- Não substitua o original; nenhuma transcrição secundária prova completude ou vigência.

Saída sugerida por análise: `evidence_links[]`, `candidate_requirements[]`, `candidate_findings[]`, `coverage_report`, `license_review_needed`, `no_canonical_changes:true`.
