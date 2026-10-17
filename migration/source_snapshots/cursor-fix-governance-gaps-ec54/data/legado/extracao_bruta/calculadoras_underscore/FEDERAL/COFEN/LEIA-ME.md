# FEDERAL / COFEN — Resoluções atomizadas (V1, 10/10/2026)

Gerado a partir dos PDFs do Diário Oficial da União que estavam na pasta `cofen` do acervo (cópias de 09/10/2026). Segue o padrão já usado em `BR_FED_COFEN_RES_2024_N_00736` (NORMA, ATOMOS, VALIDACAO, MANIFESTO).

Cada pasta `BR_FED_COFEN_RES_<ano>_N_<número>` contém:
- `*_NORMA_V1.json`: identidade, ementa, publicação no DOU (edição, data, códigos de autenticidade), cláusula de vigência, normas citadas e licença de uso.
- `*_ATOMOS_V1.jsonl`: um registro por dispositivo (ementa, preâmbulo, cada considerando, artigo, parágrafo, inciso, alínea e anexo), com transcrição literal do DOU e hash SHA-256 do texto.
- `*_VALIDACAO_V1.json`: controles executados e achados.
- `*_TEXTO_DOU_V1.txt`: texto integral extraído do DOU.
- `*_DOU_FONTE.pdf`: PDF de origem.
- `MANIFESTO_V1.json`: SHA-256 de todos os arquivos.

Registros consolidados (no formato das abas do PMO) estão em `REGISTROS/`.

## Pendências (valem para todas)
- Atomização automática: requer revisão humana da segmentação e da literalidade.
- Pesquisa de alterações e revogações posteriores não realizada.
- Anexos (801, 805, 810) ficaram como um único átomo; atomização interna pendente.
- Resolução 803 não foi encontrada no acervo; 736 já existia e não foi refeita.
- O campo "paginas_no_arquivo_fonte" lista as páginas do PDF inteiro, que pode conter outros atos.
- Relações normativas extraídas por padrão de texto; classificação (revoga/altera/cita) a conferir.
