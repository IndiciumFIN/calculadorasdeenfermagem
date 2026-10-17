# Evidência — Resolução Cofen nº 736/2024: conferência do sha256 com a fonte oficial

Data da verificação (UTC): 2026-10-10T19:40:11Z (16:40 BRT). Ferramenta de texto: pdftotext version 25.03.0.

## Veredito
IDENTICO: a cópia local (sha256 3fb4e597f053aefeb1aadf9b50c1ace53c32ca687454c28184814741677d7a49, 718575 bytes) é byte a byte igual ao PDF baixado agora de cofen.gov.br. Em relação à publicação oficial no DOU (in.gov.br), é MESMO CONTEÚDO COM BYTES DIFERENTES (texto extraído idêntico).

## Arquivos
- **copia_local_biblioteca (= mapeada para Calculadoras-de-Enfermagem/cofen/BR_FED_COFEN_RES_2024_N_00736 pela matriz)**
  - /workspace/doencas/protocolos_enfermagem/raw/pdfs/Resolucao_Cofen_no_736_2024_Processo_de_Enfermagem.pdf
  - 718575 bytes — sha256 `3fb4e597f053aefeb1aadf9b50c1ace53c32ca687454c28184814741677d7a49`
- **oficial_cofen_download_novo**
  - https://www.cofen.gov.br/wp-content/uploads/2024/01/Resolucao-736-2024.pdf
  - 718575 bytes — sha256 `3fb4e597f053aefeb1aadf9b50c1ace53c32ca687454c28184814741677d7a49`
  - Cabeçalhos HTTP:
```
HTTP/2 200 
date: Sat, 10 Oct 2026 19:40:10 GMT
content-type: application/pdf
content-length: 718575
set-cookie: HWWAFSESID=6413273630c5a42ea7; path=/
set-cookie: HWWAFSESTIME=1791661210954; path=/
last-modified: Tue, 23 Jan 2024 11:35:41 GMT
etag: "65afa48d-af6ef"
accept-ranges: bytes
server: CW
```
- **oficial_dou_in_gov_br (pagina 74 da Secao 1 de 23/01/2024)**
  - https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=515&pagina=74&data=23/01/2024&captchafield=firstAccess
  - 736965 bytes — sha256 `f302110a6564257b782c6286908b5bdcb1897436c3c15998f138cabd8d8fd3a4`
  - Cabeçalhos HTTP:
```
HTTP/2 200 
date: Sat, 10 Oct 2026 19:40:35 GMT
content-type: application/pdf
content-length: 736965
vary: Accept-Encoding
x-azion-request-id: e8d91e26dd1be430ba1db0f5b1821d2c
x-azion-edge-location: SJC
debug: 4
set-cookie: az_asm=WN/YIANmYeBWxpVA8YBKwjGjAfeiuQG3h6BHQH+oEfpk2T/y9IAcnRz4xjIIcaOpI8P+D2EWI293vL9c; Domain=pesquisa.in.gov.br; Path=/; Max-Age=86400; Secure; HttpOnly; SameSite=Lax
set-cookie: az_botm=e8d91e26dd1be430ba1db0f5b1821d2c; Domain=pesquisa.in.gov.br; Path=/; Max-Age=86400; Secure; HttpOnly; SameSite=Lax
expires: Sat, 10 Oct 2026 19:40:35 GMT
cache-control: max-age=0
```
- **oficial_cofen_versao_SEI (impressao web do documento SEI 0208733, CRC F5190F43)**
  - https://www.cofen.gov.br/wp-content/uploads/2024/01/Resolucao-Cofen-no-736-2024-Dispoe-sobre-a-implementacao-do-Processo-de-Enfermagem-em-todo-contexto-socioambiental-onde-ocorre-o-cuidado-de-enfermagem.pdf
  - 183424 bytes — sha256 `8a8a9ecb5987a308f8e51fa2a291ea19c9284c9712300744f144c7ba48c3329e`
  - Cabeçalhos HTTP:
```
HTTP/2 200 
date: Sat, 10 Oct 2026 19:40:33 GMT
content-type: application/pdf
content-length: 183424
set-cookie: HWWAFSESID=ec0c673a1498d08c63; path=/
set-cookie: HWWAFSESTIME=1791661233149; path=/
last-modified: Tue, 23 Jan 2024 11:33:45 GMT
etag: "65afa419-2cc80"
accept-ranges: bytes
server: CW
```

## Comparações
- copia_local × oficial_cofen_download_novo: **IDENTICO (mesmos bytes)**
- copia_local / oficial_cofen × oficial_dou_in_gov_br: **MESMO CONTEUDO, BYTES DIFERENTES**
  - pdftotext (modo -layout e modo padrão) produz texto IDÊNTICO byte a byte nos dois PDFs (sha256 do texto padrão 787d8d5e…, layout 6893f965…). O PDF do Cofen é a mesma página 74 do DOU regravada pelo PDFium (metadados e estrutura diferentes, conteúdo textual igual).
- oficial_dou_in_gov_br (corpo da resolução) × oficial_cofen_versao_SEI (corpo): **MESMO CONTEUDO NORMATIVO, DIFERENCAS TIPOGRAFICAS (documento SEI, nao e a publicacao oficial)**
  - Corpo da resolução: 1512 x 1519 tokens, similaridade 0,9957. Diferenças: (1) DOU 'Nº 736, DE' x SEI 'Nº 736 DE' (vírgula); (2) DOU 'resolve' x SEI 'RESOLVE' (caixa); (3) DOU 'interrelacionadas' x SEI 'inter-relacionadas'; (4) hífen x travessão (–) em várias alíneas; (5) cabeçalhos/rodapés do SEI (paginação 1/4, 2/4, URLs, código verificador). Assinaturas: DOU traz nomes impressos; SEI traz assinatura eletrônica. Nenhuma diferença de conteúdo normativo encontrada.

## Observações
- O prefixo 3fb4e597 citado na matriz (linha RES|736|2024) confere.
- Conferência do código de autenticidade 05152024012300074 no site do DOU não feita (exige interação no formulário); o PDF foi obtido do servlet oficial pesquisa.in.gov.br.
- NORMA_V2.json do pacote 736 (Calculadoras) registra conferencia_literal_dou = PENDENTE; esta evidência pode ser usada para fechá-la, após revisão humana.
