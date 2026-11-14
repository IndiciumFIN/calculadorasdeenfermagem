# CKO W7 v0.2.8 — conteúdo curricular somente atomizado

**ESCOPO: somente currículo.** Esta versão deriva 985 candidatos CURRICULUM_SOURCE_ITEM preservando as redações originais das 985 linhas curriculares disponíveis, sem inventar ementas, claims, módulos, carga ou aulas.

## Conteúdo derivado
- 985 registros com atom_text original, source item, program_id, institution_id, item_type, data e status de temporalidade
- 1.514 relações candidatas entre item e 182 tópicos
- 114 programas cadastrados; 83 com itens, 31 sem itens
- 919 itens de fontes atuais e 66 de fontes históricas; 191 objetivos parafraseados expressamente marcados
- 6 itens sem mapeamento temático
- 52 grupos de títulos repetidos entre programas, preservados separadamente
- 162/162 itens do recorte anterior W7 conferidos por id + título + programa

Os originais são os 4 JSONL do Drive na pasta https://drive.google.com/drive/folders/1xR1Cy2s70TMiZhb84G4xMOmGrFGnq2lo. Seus tamanhos e hashes SHA-256 calculados no corpus local estão no arquivo SUMMARY. Arquivos foram relidos do Drive para gerar esta versão.

**Cada átomo é uma linha de origem curricular, não claim ou fragmento clínico aprovado.** O arquivo original raw_description está vazio em 985/985 linhas; não é possível preencher detalhes de ementa a partir dos títulos. A classificação em tópicos é candidata, sem equivalência semântica automática. Títulos iguais de instituições diferentes não são deduplicados.

O corpus de EvidenceAtoms não foi importado nem automaticamente vinculado ao currículo: seu namespace de tópicos é distinto. Respeitam-se HOLD_CURRICULUM_IDENTITY_RIGHTS_REVIEW, HOLD_SEMANTIC_MAPPING e NO_GO. Sem geração editorial, parsers, agentes, Supabase, merge ou deploy.
