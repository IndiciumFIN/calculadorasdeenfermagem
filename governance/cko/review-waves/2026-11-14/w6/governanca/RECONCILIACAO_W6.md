# Governança W6 — reconciliação e limites

## Fontes recuperadas e observadas
- **Google Drive**: cinco HTMLs originais foram recuperados byte a byte; metadados e hashes no registro `dados/LEGACY_ASSET_RECOVERY.json`. Dados extraídos desses arquivos são **históricos** e podem conter erros, material sem direitos confirmados, idiomas trocados e afirmações clínicas não verificadas.
- **GitHub (workspace disponível)**: `IndiciumFIN/dev-chatgpt-workspace`, contratos de bibliotecas, ferramentas clínicas, conteúdo de segurança do paciente e artigo histórico de curiosidades sobre Aldrete. O conteúdo de origem da biblioteca CME mantém identidade própria e não foi alterado.
- **GitHub (repositório clínico privado)**: `IndiciumFIN/calculadorasdeenfermagem` passou a retornar 404 no acesso atual, inclusive às PRs #64/#66/#67 e branch W4.1. **Não criar PR ou alegar publicação W6** sem resposta de sucesso e verificação de conteúdo; não usar o repositório público em substituição por conveniência.
- **Supabase Calculadoras-Smart (somente leitura)**: `cko_evidence.sources` possui `SRC-COFEN-RES-736-2024`, `SRC-COFEN-RES-754-2024` e `SRC-ANVISA-RDC-36-2013` com `PENDING_BOARD_REVIEW`. `cko_regulatory.instruments` tem 736/754 mas não possui no recorte inspecionado a entrada 581/2018. `ce_platform.content_documents` encontra-se vazio na checagem prévia, não provando ausência de conteúdo em arquivos.
- **Web oficial**: fontes COFEN 581, 736, 754; RDC 36; Protocolo Cirurgia Segura MS; manual OMS. Sem cópia integral de normas, manuais ou checklists no material autoral.

## Separação formal de entidades
- `CARDIOLOGIA` = estrutura curricular especializada; não módulo de Centro Cirúrgico.
- `CENTRO_CIRURGICO` = área, com projeção didática W6 e recorte SRPA.
- `SRPA` = recorte específico referenciado no rol de especialidades de Centro Cirúrgico; unidade didática autônoma para revisão, não novo currículo aprovado.
- `CME` = biblioteca `cko.library.cme` e módulo educativo próprio `CKO-W5-CME-FUNDAMENTOS-PROCESSAMENTO`. Relação `CROSS_SPECIALTY_REFERENCE_ONLY`, não fusão.
- `Aldrete` = ferramenta clínica já encontrada no corpus histórico, não uma criação desta onda.
- `PE` = CORE reutilizável referenciado nas W3/W4, não reescrito aqui.

## Etapas de revisão antes de publicar
1. Completar tabela de localizadores com páginas/artigos, versões e hashes primários. Revisar alterações e revogações.
2. Revisar item a item as páginas legadas, idioma e acessibilidade; não normalizar artificialmente um arquivo fonte danificado.
3. Conferir direitos dos questionários/escalas/checklist por operação; diferenciar citação, adaptação e republicação.
4. Aprovação clínica por especialistas de Centro Cirúrgico e SRPA, além de revisão de documentação, direitos, LGPD e governança.
5. Só então produzir um candidato de publicação com objeto principal, derivados e históricos devidamente vinculados. **Sem migração ao Supabase e sem merge automático.**

## Matriz de decisão
`norma = fonte`; `protocolo MS = referência institucional/nacional a verificar`; `manual OMS = orientação internacional`; `HTML Drive = artefato legado`; `quiz W6 = texto editorial novo`; `SCORE = objeto clínico com gate próprio`; `CME = área separada`. Toda equivalência automática é proibida.
