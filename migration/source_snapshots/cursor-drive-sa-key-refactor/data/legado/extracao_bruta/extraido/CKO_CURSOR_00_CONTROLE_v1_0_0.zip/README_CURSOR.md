# CKO · Fragmentação íntegra para Cursor — v1.0.0

**Origem:** [extracao bruta Grok Bot Danadão](https://drive.google.com/drive/folders/1l519_P-9o6bnQcItydKvEEDpEYeE8R8s)

**Modo:** análise privada/offline, candidatos. **Originais no Drive não alterados.** Nenhuma WO de produção é criada ou executada. Não enviar estes conteúdos automaticamente a APIs/LLMs externos sem checagem de licença e privacidade.

## Como funciona

- `ANALISE`: PDFs em sequências contíguas de **25 páginas**, mais `.pages.jsonl` com texto integral de cada página, números 1-based e SHA-256. O PDF fragmentado, e principalmente o original, prevalecem sobre o texto extraído quando houver divergência de layout.
- `RECONSTRUCAO_EXATA`: blocos binários consecutivos do PDF original, com SHA-256 por bloco e checksum original. Reconstituição preserva **exatamente** os bytes do PDF original.
- `CONTROLE`: manifesto mestre, referência ao Drive, relatório de QA, scripts e orientações para o Cursor.

**Não misture os métodos:** concatenar partes `ANALISE/*.pdf` **não** reconstrói os bytes originais. Para reconstrução bit a bit use `RECONSTRUCAO_EXATA/*.partNNNN` com `verify-binary`.

## Documentos prioritários

| Código | Documento | Páginas | PDFs de análise | Binários originais | QA |
|---|---|---:|---:|---:|---|
| `VACINACAO_MANUAL` | Manual de Normas e Procedimentos para Vacinação (2ª ed.) | 296 | 12 | 2 | PASS |
| `SAUDE_MULHER` | Protocolos da Atenção Básica — Saúde das Mulheres | 231 | 10 | 2 | PASS |
| `ISOLAMENTO` | Guideline for Isolation Precautions | 211 | 9 | 2 | PASS |
| `HIPERTENSAO` | Diretrizes Brasileiras de Hipertensão Arterial 2020 | 143 | 6 | 1 | PASS_WITH_WHITESPACE_NOTE |
| `NEWS2` | NEWS2 RCP Final Report 2017 | 77 | 4 | 1 | PASS |
| `CALENDARIO_VACINAL_2026` | Instrução Normativa — Calendário Nacional de Vacinação 2026 | 60 | 3 | 1 | PASS |

**Observações:** no PDF de hipertensão, 7 páginas sofrem apenas diferença de whitespace na reextração do PDF dividido; sua renderização visual nas páginas de controle passou e a transcrição se baseia no original. No protocolo de saúde da mulher, 7 páginas tinham pouco texto extraível; inspecionar o PDF visualmente antes de assumir que não contêm conteúdo. **OCR não foi executado.**

## Pré-requisitos do Cursor

Python 3.10+ e `python -m pip install pymupdf pypdf` (instalação local). Não é necessário login em APIs nem chaves de acesso para verificar arquivos já extraídos.

## Procedimento no Cursor

1. Extraia primeiro o ZIP `CONTROLE`. Descompacte somente o ZIP `ANALISE` relativo ao tema; mantenha a árvore `SLUG/*`. Para reconstituir o original, extraia o ZIP `RECONSTRUCAO_EXATA` correspondente.
2. Execute `python fragmentar.py verify-pdf <pasta-extraida/SLUG>` para testar a integridade e a sequência dos trechos PDF/texto (sem o original). Com original disponível: acrescente `--source <original.pdf>` para confrontar o SHA-256 original.
3. Para partes binárias: `python fragmentar.py verify-binary <pasta-extraida/SLUG> --rebuild <saida_original.pdf>`. Isso prova a equivalência byte a byte pelo SHA-256 original.
4. Leia `INVENTARIO_E_QA.json` e `SLUG/MANIFEST.json`. Navegue pelos intervalos P0001-P0025, etc. Cada linha em `.pages.jsonl` referencia a página original, jamais renumere os dispositivos automaticamente.
5. Produza **relatórios candidatos**, links entre fonte e evidência e lista de problemas; **não** altere Master Data, Regulatory Core, GitHub, Drive ou banco sem Task Definition qualificada, WO válida e execução pelo Kernel.
6. Não conclua vigência, licença, validade clínica ou aderência normativa apenas com hash, PDF ou texto extraído. Precisa de source/rights/aplicabilidade e validadores.

## Limites da execução

- Este recorte contém 6 PDFs maiores/mais extensos encontrados. Não é backup integral da pasta.
- Folders temáticos vazios ou apenas com `raw/` foram mantidos intactos no Drive. Itens enviados à lixeira não foram restaurados ou recriados.
- Os ZIPs de análise são independentes por documento e não homologam normas ou algoritmos clínicos.
