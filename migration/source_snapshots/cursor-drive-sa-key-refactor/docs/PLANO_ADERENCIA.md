# Plano de aderência canônica

Estado observado: branch `cursor/fix-governance-gaps-ec54`. Gate Agregador do PR passou na run `38690629942`, antes dos lotes de fração. Este documento não autoriza produção, não qualifica tarefa e não substitui Work Order.

Automático significa executar a próxima onda cujo gate esteja verde e parar no primeiro gate vermelho. Não significa promover, copiar ou apagar sem o procedimento qualificado.

## Autoridade

A escrita canônica entra por `python -m packages.cli.kernel`. Procedimentos qualificados hoje: `obter`, `atomizar`, `validar`, `retirar`, `registrar-find`, `vincular-find`, `analisar-find`, `corrigir-find`, `encerrar-find`.

T01, T02, T04 e T07 continuam não qualificadas. `ingest`, `process`, `pipeline run`, `registry add`, `registry set-status` e `scripts/migrar_drive.py` saem com código 2 antes de gravar.

O Git versiona código, contratos e governança. O corpus canônico não está homologado. O Supabase é destino previsto, não a autoridade atual. `authorized_by` continua texto.

## Onda 0 — já no checkout

Portas de escrita do CLI antigo fechadas. `FIND-0001` e `FIND-0002` abertos. 104.668 candidatos em `Não verificado`. 7.679 linhas em quarentena. 336 identificadores com textos diferentes, sem escolha de lado. 109 itens do Drive relidos como ausentes na lixeira recuperável. Quatro raízes do Drive com exclusão bloqueada.

## Onda 1 — fração dos arquivos grandes e suprimentos

`mesh`, `icd11` e `medicamentos` tiveram a listagem fechada. A página seguinte de `mesh` e de `icd11` voltou vazia; cada título exato fechou sem `nextPageToken`. Em `medicamentos` e em `suprimentos`, a segunda página trouxe arquivos e não trouxe página seguinte.

Cada lote passou por `obter`, `atomizar`, `validar` e `retirar`. Classe `REFERENCIA`, zero átomos. ICD-11 foi copiado sem alteração. As pastas `raw` permanecem.

A decisão de volume para arquivo a partir de 50.000.000 bytes é fracionar em partes de 40.000.000 bytes. O arquivo inteiro não entra no Git. A concatenação das partes precisa repetir o SHA-256 lido no `obter`. Cinco JSON passaram por isso e a releitura devolveu ausência: preços CMED, NDC, USDA SR Legacy, produtos para saúde da Anvisa e CATMAT das classes 6510, 6515, 6530 e 6532. Os sete arquivos de `suprimentos` abaixo do limite também foram copiados inteiros e a origem está ausente.

A raiz da extração bruta fechou em 18 pastas e um zip de controle. Todas foram consideradas. `protocolos_enfermagem` é ato, sem extrator, e o PDF clínico não entra no Git público. As pastas `raw` e as cascas dos temas permanecem. O zip `CKO_CURSOR_00_CONTROLE` é controle de análise de PDF clínico e permanece no Drive.

`dispositivos` fechou a listagem de arquivos. Os três abaixo de 50 MB foram copiados; o JSON grande já estava fracionado. A subpasta `raw` permanece. Os oito arquivos da raiz de `atomizado` e seis documentos de `revisao` foram copiados, com zero átomos. Sete tabelas clínicas transcritas de `revisao` permanecem no Drive.

O manifesto de `atomizado/mesh` repete o SHA-256 dos quatro arquivos MeSH já implantados. O `descritor_mesh.jsonl` é árvore derivada, não a mesma cópia, e não foi descartado.

A barra do que pode entrar, com listagem fechada, está em `data/legado/progresso_drive.json`: 144 de 144. Isso não é 100% do Drive.

## Onda 2 — duplicidade por hash

Nome e tamanho iguais não são identidade. Conteúdo idêntico em caminhos diferentes é uma cópia, registrada uma vez. O mesmo nome com hashes diferentes não tem lado escolhido e não sai do Drive.

Os dez zip e gzip de `extracao_bruta` foram extraídos em bytes. O compactado permanece. Oito membros repetem o SHA-256 de uma cópia já implantada e não foram gravados de novo, entre eles os seis CSV do CID-10. Três membros passam de 50 MB e ficaram fracionados, com a concatenação repetindo o SHA-256: MeSH `desc2026` (312.952.703 bytes, 8 partes), NDC (245.353.596 bytes, 7 partes) e Anvisa registrados (113.538.797 bytes, 3 partes). ICD-11 saiu sem alteração. A análise de cada compactado está em `extraido/*/analise.json`.

As pastas `raw` foram cruzadas com as Work Orders `0001` a `0040`. Nenhum arquivo tinha o mesmo nome e o mesmo tamanho. A alternativa para esse caso é gravar o arquivo em `*/raw/`, sem substituir a cópia derivada. As ordens `0068` a `0071` fizeram isso com 50 arquivos, zero átomos, e a origem foi para a lixeira. Zip e gzip entraram fechados. O HTML da portaria entrou porque o anexo tinha o nome do destino e 56.295 bytes. O XML do MedlinePlus entrou depois da confirmação do aviso de download do Drive. Arquivo a partir de 50 MB continua fracionado. Ato sem extrator entra como `DOCUMENTO` ou `REFERENCIA`, com zero átomos. Tabela transcrita do próprio projeto segue o mesmo caminho das que já estão em `sinais_vitais` e `sepse`. Texto de página de PDF de editora fica fora do Git. Esvaziar a lixeira continua só com uma pessoa.

As ordens `0076` a `0079` copiaram as 30 partes do atlas (até 20 MB cada), os manifestos e os dois scripts de reconstrução. Zero átomos. Os scripts não foram executados e o zip não foi remontado. A pasta do atlas ficou vazia e foi para a lixeira. As ordens `0080` a `0083` copiaram os LEIA-ME e os zips de PAR e OS, extraíram os membros em bytes e esvaziaram essas duas pastas. As ordens `0084` e `0092` a `0094` copiaram os zips de portaria, legislação, outros e edital abaixo de 50 MB e extraíram os membros. Seis resoluções explodidas foram copiadas pelas ordens `0086` e `0095` a `0097`. Planilha nativa e arquivos da ESTEIRA, só do dono, falharam no download público e seguiram para o lote seguinte.

As ordens `0072` a `0075` copiaram os 129 arquivos que restavam com listagem fechada: tabelas transcritas, índices de protocolo, PDFs oficiais, evidência da COFEN 736, cabeçalhos das fontes, o zip de controle e os jsonl derivados em `atomizado/`. Zero átomos. Seis jsonl passam de 50 MB e ficaram fracionados, com a concatenação repetindo o SHA-256. O zip de controle foi extraído em bytes; os cinco membros são texto de controle, não os zips clínicos que ele indexa. Download com resposta 500 repete até três vezes e continua fechado se persistir. Na pasta do Drive permanecem a pasta `revisao` e, dentro dela, `fontes`, com cinco PDFs de editora (NEWS2 RCP 2017, Sepsis-3 JAMA 2016 e Diretrizes Brasileiras de Hipertensão 2020). Esses originais não foram para a lixeira.

`atomizado/mesh` já teve a comparação: os hashes de origem conferem com a cópia implantada e o jsonl derivado permanece. As outras pastas filhas de `atomizado` ainda precisam dessa comparação, arquivo a arquivo. A árvore COFEN tem 249 pares de mesmo nome e tamanho entre `FEDERAL/COFEN` e `NORMATIVOS/FEDERAL/COFEN`; os dois hashes precisam existir antes de qualquer descarte. Os 336 conflitos do legado continuam sem fusão.

## Onda 3 — lote de referência

Só começa com listagem fechada. Arquivo a partir de 50.000.000 bytes entra fracionado, em partes de 40.000.000 bytes, com o SHA-256 original conferido na concatenação. Cada lote usa quatro Work Orders, nesta ordem: `obter`, `atomizar`, `validar`, `retirar`.

Classes `REFERENCIA`, `SCRIPT` e `DOCUMENTO` atomizam como não aplicável, com zero átomos, e o arquivo permanece. Ato sem extrator não gera átomo e não vai para a lixeira. ICD-11, se a listagem fechar, é copiado sem alteração (CC BY-ND). Texto clínico e PDF de protocolo não entram no repositório público como átomo normativo.

`retirar` não chama o Drive. A lixeira é `trash_file` só para identificadores presentes no arquivo de autorização daquela Work Order. A releitura precisa devolver `Requested entity was not found` para o livro registrar `AUSENTE`. A lixeira é recuperável. Esvaziar a lixeira está bloqueado: somente uma pessoa pode fazer isso. Pasta sem filhos vai para a lixeira recuperável. Pasta com arquivo ou subpasta fica. A raiz da extração bruta permanece.

## Onda 4 — Supabase

Dois projetos permanecem. Nada é apagado.

No projeto ativo, o schema regulatório está vazio de instrumentos, o atlas tem 65.200 átomos de anatomia BodyParts3D e o editorial tem provas. Isso não é o corpus normativo. No projeto restaurado, leis em nome, catálogo de provas e quatro PDFs de mesmo tamanho continuam sem hash de identidade.

A migration `supabase/migrations/20261014000000_governance_fixes.sql` está versionada e não foi aplicada. Aplicar é ação humana. Antes disso, a leitura pública antiga continua. Depois disso, publicação depende de `autorizacao_publicacao`, não do status `Vigente`.

Não há tarefa qualificada para gravar no Supabase. Os 104.668 candidatos não são copiados para tabela de produção. O gateway DeepSeek não exige Work Order e usa temperatura padrão 0.1; o guard de referência não é implantado nesta onda.

## Onda 5 — frontend canônico

O site em `src/` tem cinco arquivos de estrutura. Completo, neste plano, é a casca que só calcula instrumento publicado.

- Tokens de `packages/design-system/tokens.json`: `#1A3E74`, `#1E4D8C`, `#163269`.
- A página inicial explica o estado: candidato não é calculadora vigente.
- A rota de registro lista só item com publicação autorizada. Enquanto a migration não existir no banco, a lista fica vazia de propósito.
- A rota de calculadora recusa conta sem identificador canônico vindo do Registry. Nenhuma fórmula clínica é escrita no código como se fosse norma.
- O builder continua composição visual, sem virar segunda fonte de átomos.

Calculadora clínica de catálogo inteiro espera instrumento com fonte oficial, data de verificação e autorização de publicação. Isso não está no corpus atual.

## Gates que interrompem a onda

1. Listagem incompleta.
2. Hash da cópia diferente do arquivo lido.
3. Mesmo nome e conteúdo diferente.
4. Fração cuja concatenação não repete o SHA-256 original, ou parte com 50.000.000 bytes ou mais.
5. Licença desconhecida, ou cópia que exigiria alteração de ICD-11.
6. Tarefa fora dos nove procedimentos qualificados.
7. Work Order inválida, ou `FIND` crítico aberto quando o passo promove status.
8. Gate Agregador do PR em falha.
9. Tentativa de esvaziar lixeira, aplicar migration, ativar proteção de branch ou declarar `FOUNDATION_COMPLETE` por código.

Proteção da `main`, aplicação da migration, esvaziamento da lixeira e assinatura institucional de `authorized_by` continuam humanas. Identity Issuer e Master Registry continuam não comprovados. As listas de estado de `docs/REGISTRY.md` e de `packages/cli/registry.py` não são unificadas por este plano.
