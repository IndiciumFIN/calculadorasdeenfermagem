# CKO — MedlinePlus XML (metadados e links; sem republicação)

**Status:** `TECHNICAL_CANDIDATE / HOLD_RIGHTS / HOLD_EDITORIAL / NO_PUBLICATION`. WO #44; dependente PR #40.

## Fontes primárias
- [MedlinePlus XML Files — NLM](https://medlineplus.gov/xml.html)
- [MedlinePlus Health Topic XML File Description](https://medlineplus.gov/xmldescription.html)
- [MedlinePlus — Uso e direitos](https://www.medlineplus.gov/about/using/usingcontent/)
- Contrato `contracts/fontes/medlineplus.json`; política `KERNEL-POLICY-015` v1.1.0.

## Operações aceitas
- Entrada XML `<health-topics total="N" date-generated="...">` ou `dategenerated="..."` contendo `<health-topic>` com `id`, `title`, `url`, `language`, grupo e site (metadados essenciais).
- Pega somente título de tópico, URL canônica, idioma, IDs, títulos de grupos, IDs MeSH e vínculos candidatos com outros tópicos / idioma.
- Valida idioma, URL HTTPS com host MedlinePlus, unicidade de IDs, total informado e integridade de vínculos internos; `defusedxml` evita expansão de entidades, não faz network fetch de DTDs.
- Uma entrada inválida rejeita a **coleta inteira**, sem mistura de registros aprovados e rejeitados. Para feed parcial, `verify_internal_links=False` preserva links como candidatos, nunca como vínculos homologados.
- Limite de entrada 64 MB; o XML completo diário é publicado em torno de 29 MB pela NLM.
- Interface: `parse(xml, source_id="...", document_id="...")`, com IDs fornecidos pela etapa de proveniência.

## Não incluído
- Nenhum `full-summary`, imagem, site externo, sinônimo, RSS, artigo ou conteúdo protegido é reaproveitado na saída. A fonte deve receber atribuição quando utilizada.
- Não há promoção de claims, execução de regras clínicas, atualização de Supabase ou publicação no site.
- Referências MeSH externas geram **IDs candidatos**, não vínculos validados com vocabulário oficial local.
- `schema_validator` ainda falha em testes negativos; sua política permanece rejeitada no Kernel.
- Não houve teste de ingestão com dados completos externos nem revisão jurídica por operação.

## Critérios de continuidade
- Conferir versões, alterações e licenças por fonte/uso (NLM/terceiros), testar amostras oficiais autorizadas.
- Consolidar schema de tópicos e links canônicos no dicionário/metamodelo automatizado com invariantes.
- Revisar mapeamentos, homologar direitos e editorial; permitir publicação **somente por aprovação independente**.
