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

`protocolos_enfermagem` não começou: é ato, sem extrator, e o PDF clínico não entra no Git público.

Pastas ainda sem lote completo: `revisao`, `atomizado`, `protocolos_enfermagem`, `raw`, `dispositivos`. A raiz de `revisao` e os oito arquivos na raiz de `atomizado` têm listagem fechada e ainda não têm lote. A listagem de `dispositivos` ainda tem página seguinte; o JSON grande dessa pasta já foi fracionado.

A barra da listagem fechada está em `data/legado/progresso_drive.json`: 126 de 147 arquivos, 86%.

## Onda 2 — duplicidade por hash

Nome e tamanho iguais não são identidade. Conteúdo idêntico em caminhos diferentes é uma cópia, registrada uma vez. O mesmo nome com hashes diferentes não tem lado escolhido e não sai do Drive.

`atomizado` só entra em comparação arquivo a arquivo com as cópias já versionadas. A árvore COFEN tem 249 pares de mesmo nome e tamanho entre `FEDERAL/COFEN` e `NORMATIVOS/FEDERAL/COFEN`; os dois hashes precisam existir antes de qualquer descarte. Os 336 conflitos do legado continuam sem fusão.

## Onda 3 — lote de referência

Só começa com listagem fechada. Arquivo a partir de 50.000.000 bytes entra fracionado, em partes de 40.000.000 bytes, com o SHA-256 original conferido na concatenação. Cada lote usa quatro Work Orders, nesta ordem: `obter`, `atomizar`, `validar`, `retirar`.

Classes `REFERENCIA`, `SCRIPT` e `DOCUMENTO` atomizam como não aplicável, com zero átomos, e o arquivo permanece. Ato sem extrator não gera átomo e não vai para a lixeira. ICD-11, se a listagem fechar, é copiado sem alteração (CC BY-ND). Texto clínico e PDF de protocolo não entram no repositório público como átomo normativo.

`retirar` não chama o Drive. A lixeira é `trash_file` só para identificadores presentes no arquivo de autorização daquela Work Order. A releitura precisa devolver `Requested entity was not found` para o livro registrar `AUSENTE`. A lixeira é recuperável. Esvaziar a lixeira é ação humana. A pasta raiz permanece mesmo quando os filhos saíram.

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
