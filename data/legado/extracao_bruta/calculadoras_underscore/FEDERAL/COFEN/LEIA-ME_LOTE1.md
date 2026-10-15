# FEDERAL / COFEN: Lote 1, Pareceres Normativos e Notas Técnicas (V1, 10/10/2026)

Fonte: site do Cofen, API WordPress (`/wp-json/wp/v2/posts`), categorias "Pareceres Normativos" (id 612, 36 posts) e "Nota Técnica" (id 920, 17 posts). Foram baixados a página HTML de cada post e os PDFs do bloco "Anexos" da página e dos links `wp-content/uploads`. As resoluções não entram neste lote.

Pastas: `PARNORM/` (categoria 612) e `NOTATEC/` (categoria 920). Cada ato fica em `BR_FED_COFEN_<TIPO>_<ano>_N_<número>`. Quando o post da categoria 612 não é um Parecer Normativo, o código usado é o do tipo real: PARCONS (parecer de conselheiro), PARCT (câmara técnica), PARCOM (comissão) ou PARJUR (jurídico). Atos sem número usam `SN_<slug>`.

Arquivos por ato:
- `*_NORMA_V1.json`: identidade, ementa, publicação (site, PDFs, SEI, menções ao DOU), cláusula de vigência, normas citadas, licença (Lei 9.610/1998, art. 8, IV) e contagem.
- `*_ATOMOS_V1.jsonl`: um registro por dispositivo, com o campo `conferencia_pdf` em cada átomo do site.
- `*_VALIDACAO_V1.json`: controles, achados e a conferência dispositivo a dispositivo.
- `*_TEXTO_FONTE_V1.txt`, `*_PAGINA_SITE.html`, `*_CONTEUDO_SITE_API.json`, `*_PDF_SITE.pdf` (+ `_TEXTO_V1.txt` ou `_TEXTO_OCR_V1.txt`), `*_ANEXO_nn_PDF_SITE.pdf`, `IMAGENS_SITE/` e `MANIFESTO_V1.json` (SHA-256 de todos os arquivos).

Códigos de achado: C001/C002 (revisão humana e pesquisa de atos posteriores, sempre pendentes), C010 (sem PDF), C011 (dispositivo do site divergente ou ausente no PDF), C012 (PDF digitalizado, conferido por OCR), C013 (PDF anexado é de outro ato), C014 (trecho do PDF sem correspondente no site), C015 (texto só no PDF digitalizado, transcrito por OCR), C020 (anexo referenciado ausente), C021 (conteúdo em imagem, com linhas por OCR), C030 (numeração com lacuna ou repetição), C031 (sequência que não começa em 1/I/a; não bloqueante), C040 (sem número), C041 (tipo diferente da categoria), C042 (publicação duplicada), C043 (número divergente).

Nenhum ato foi marcado como validado. Os rótulos são "Validado com apontamentos" (sem achado bloqueante além de C001/C002) e "Pendente de verificação". Nenhum código do DOU foi conferido no in.gov.br. Scripts em `/workspace/proj/scripts_lote1`.
