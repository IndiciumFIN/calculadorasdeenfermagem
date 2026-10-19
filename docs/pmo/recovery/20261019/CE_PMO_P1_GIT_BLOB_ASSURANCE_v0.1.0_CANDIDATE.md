# CE P1 — Crosswalk de hashes Git blob + SHA-256 (candidato)

**Escopo:** inventário recursivo read-only de snapshot local contra `files[{path,git_blob_sha1,sha256,byte_length}]` fornecidos. Calcula Git blob SHA-1 conforme cabeçalho `blob <length>\\0` + bytes e SHA-256, confere tamanho, detecta arquivos ausentes/extras, duplicatas, caminhos inválidos, symlinks e alterações durante leitura.

**Limites de afirmação:** prova igualdade do conteúdo local com um manifesto fornecido; não prova origem de manifesto, árvore Git remota, commit assinado, população original do Drive ou precisão semântica. Git SHA-1 não substitui SHA-256 e não deve sozinho servir de atestação de autenticidade.

**Comando:** `python tools/ce_agents/ce_p1_git_blob_guard.py --root SNAPSHOT --manifest manifest.json`. Saídas JSON e exit 0/2. Sem gravação.

**Testes:** 10/10 Python local PASS; 30 mutações surpresa com seed 20261019. Testa modificação, exclusão, arquivo extra, duplicação, hash Git inválido, traversal, symlink, controle positivo. CI remota deve executar após publicação.

**Riscos residuais:** manifesto comprometido; censo de população original incompleto; TOCTOU se arquivos forem alterados em simultâneo; symlinks e Unicode em plataformas heterogêneas; hashes sem assinatura; limites CPU e memória. Para remediar: checkpoint Git tree completo por commit imutável, provenance, comparação com manifesto externo de origem, sandbox/fencing e auditor independente.

**Status:** `LOCAL_CANDIDATE_TESTED` de controle complementar; P1 global não homologado, nenhuma WO produtiva admitida, nenhuma versão histórica apagada.
