# CKO W2 — Restauração dos conteúdos de ética, identificação e anotações (14/11/2026)

**DRAFT_EDITORIAL / HOLD_HUMAN / NO_GO**. Esta onda preserva os arquivos do usuário e gera candidatos locais, sem modificar Supabase, Google Drive, GitHub ou site.

## Arquivos originais restaurados

| Conteúdo | Blocos | SHA-256 do HTML do usuário | equivalência JSONL |
|---|---:|---|---|
| Ética profissional, registros e Processo de Enfermagem | 22 | `697d0fefc71cfeed13eee82f0ccee1260ce49795bd0a280417a6e045b6de7282` | 22/22 (em checkboxes há prefixo visual) |
| Identificação, assinatura e carimbo | 15 | `c8ef4b56b2df507ba361f6bab8542047f294f6c2c2f3b351693e9e4a3e1262c0` | 15/15 (em checkboxes há prefixo visual) |
| Anotações de Enfermagem: qualidade e continuidade | 21 | `62ba9c1e0de432f3ba0b918b259559087206cfc8f6d6765c71e2d61e8f449efa` | 21/21 (em checkboxes há prefixo visual) |

## Conteúdo e relações
- 58/58 blocos históricos; 58 IDs de claim legados, 28 knowledge IDs, 22 referências de átomos legados, 74 arestas bloco→átomo.
- A COFEN 564/2017 tem 9 fragmentos com SHA-256 de inner HTML armazenado no snapshot de Supabase `SNAP-MON-4758C303A935A8119D60BEAA`; snapshot SHA `4758c303a935a8119d60beaafbaa0b76e49c533f46bb04053a105a78576fb19e`. Os SHA foram recalculados no SQL somente leitura e não provam aprovação da norma.
- As 14 referências relacionadas a 545/2017, ASSLEGIS 015/2018 e guia Coren-SP 2022 ficam em `HOLD_SOURCE_BYTES` até adquirir fonte original e criar hash verificável. **Nenhum SHA inventado.**
- Três artigos preservados e ampliados, mais uma aula interdisciplinar nova, 18 questões e 18 flashcards (todos DRAFT).
- QA estrutural/adversarial 16/16 verificações locais. Não equivale a avaliação clínica ou análise jurídica exaustiva.

## Diferenças normativas relevantes
- [COFEN 564/2017](https://www.cofen.gov.br/resolucao-cofen-no-5642017/): art. 35, §1º prevê carimbo facultativo.
- [COFEN 545/2017](https://www.cofen.gov.br/resolucao-cofen-no-05452017/): art. 5º prevê obrigatoriedade em hipóteses descritas.
- [Despacho ASSLEGIS/COFEN 015/2018](https://www.cofen.gov.br/despacho-asslegis-cofen-no-015-2018/): interpretação favorável a norma especial, sem dispensar revisão atual e de contextos digitais.
- [Guia Coren-SP 2022](https://portal.coren-sp.gov.br/wp-content/uploads/2022/09/anotacao-de-enfermagem.pdf): orientação educacional, não decreto/resolução, e deve ser contextualizado com 736/2024 e 754/2024.

## Próximos gates
1. Confirmar versão/vigência e alcance 545 e 564, inclusive eventuais alterações e o papel do Despacho em 2026.
2. Recuperar bytes originais 545, Despacho e guia PDF com hash e localizadores de página verificáveis, sem enviar conteúdo protegido a IA externa.
3. Crosswalk legados `CLM`/`KA`/`NAT` com ids já existentes em CKO/NCOS; aprovar somente mediante revisão humana independente.
4. Consolidar com M08/M09 e W1 por ligação tipada, sem duplicar conteúdo ou copiar norma integral em Git público.

## Limitações técnicas
- Os 58 blocos NÃO são 58 claims clinicamente aprovados: permanecem com IDs legados e 0 recibos profissionais.
- A fonte web oficial foi consultada para os atos 545/564 e Despacho; hashes `null` onde bytes não foram recuperados localmente ou no Supabase.
- `NO_PUBLICATION`, `NO_DB_MUTATION`, `NO_MERGE`.
