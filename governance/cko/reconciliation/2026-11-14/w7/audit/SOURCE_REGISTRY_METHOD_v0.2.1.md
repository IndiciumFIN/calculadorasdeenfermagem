# Método de reconciliação de 118 fontes Drive × 157 registros Supabase — v0.2.1

1. Origem Drive: `CORPUS_CANONICO_INDIVIDUAL/01_FONTES_E_AUTORIDADES/sources.jsonl`, ID `1C7T4ZDhFLHdTifp-3XqHLSwfvAwBWh2S`, SHA-256 local `39352bc418844e563f85908cdac03f1cf1e12d01eac2ce513b9e97744187649e`. Conferidos 118 objetos JSONL.
2. Origem Supabase: `cko_evidence.sources`, consulta de leitura `SELECT source_id, official_uri, title, authority_level, accreditation_status`; 157 objetos, sem modificação.
3. Preferência: `source_id` exatamente igual. Se não houver, comparar URI normalizada de forma conservadora (scheme/hostname em lowercase, `www` opcional, barra final e fragmento removidos). Sem assumir `http`↔`https` equivalentes.
4. Se uma URI corresponder a dois registros, marcar `AMBIGUOUS_URI_ALIAS`; se um só, `URI_ONLY_ALIAS_CANDIDATE`; sem match, `NO_MATCH`. Nunca concluir identidade sem validação humana da jurisdição, versão, autoridade e vigência.
5. Só públicos: IDs, títulos, URLs de fontes e etiquetas de status de direitos. Não transportar evidências textuais, artigos integrais, trechos normativos, documentos anexos ou atributos sensíveis do banco.
6. `NO_MATCH` descreve **ausência de correspondência direta nesse catálogo**, não inexistência ou incorreção da fonte; os 157 registros incluem domínios alheios ao corpus curricular de enfermagem.
7. O status atual de rights e o de acreditação Supabase são **metadados de origem**, não concessão de licença nem homologação.
8. Os achados e a fila de WOs de v0.2.0 permanecem como registro histórico. Atualizações são aditivas em arquivos `*_DELTA_v0.2.1`, sem promover nenhum objeto.
