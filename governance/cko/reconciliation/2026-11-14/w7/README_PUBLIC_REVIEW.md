# CKO W7 — reconciliação canônica (metadados para revisão pública)

**DRAFT / HOLD_CURRICULUM / HOLD_NORMATIVE / HOLD_RIGHTS / HOLD_CLINICAL / NO_GO**

Este diretório é uma entrega de **metadados de auditoria**, publicada por decisão do responsável pelo repositório. Não é material clínico validado, nem autoriza reutilização de documentos de terceiros.

## Evidências

- Corpus de origem consultado: 118 fontes, 124 documentos, 28.001 átomos de evidência, 9.102 associações candidatas. O corpus completo NÃO está neste commit.
- M08/M09: 46 vínculos `CLAIM -> EVIDENCE_ATOM` conferidos contra ID fonte, documento, locador e hashes; validação de integridade, não de conteúdo clínico.
- Currículo: 17 programas selecionados por IDs de especialidade, incluindo 12 programas com 162 itens curriculares recuperados, 274 mapeamentos candidatos e 30 contextos W4/W5/W6. Nenhuma grade institucional é adotada como grade aprovada do produto.
- W5: 8 átomos normativos sem hash de fragmento primário; W6: 6 fontes sem hash de fragmento.
- Cardiologia: 10 UCs / 51 módulos / 295 tópicos em grade candidata distinta, UC08 em conflito com UC07 e UC09.

## Conteúdo versionado

O ZIP é preservado byte a byte; os sete arquivos de dados e o README internos também estão expandidos para diff e revisão em GitHub. Não contém PDFs originais, HTMLs históricos, textos normativos completos ou dados de pacientes.

- Arquivo: `CKO_W7_RECONCILIACAO_CANONICA_20261114.zip`
- Tamanho: 18674 bytes
- SHA-256: `456f05b7a7bdd034b58bf7ab1cab16c59a2460ee44f9cd759d17e46aabab14fd`
- SHA-1 Git blob: `e5645b32882bddfc73f6e7544c8a5838bfdf0489`

## Gates independentes

- Publicar **metadados de revisão** no Git público: permitido por instrução explícita do mantenedor nesta etapa.
- Promover claims, escalas, regras clínicas, fontes sem direitos ou publicar conteúdo no site: **NÃO permitido**.
- Efetuar merge para `main`: **NÃO autorizado** até os critérios de revisão e CI.
- Mudar configurações de rulesets do repositório: **NÃO realizado**.

## Dependências / referências

- [M08/M09 PR #39](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/39)
- [W4.1 PR #66](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/66)
- [W5 PR #67](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/67)
- [W6 PR #68](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/68)

Status final permanece `HOLD_HUMAN` para currículo, direitos, conteúdo clínico e vigência normativa.
