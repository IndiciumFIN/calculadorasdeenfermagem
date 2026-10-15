# Plano de aderência canônica

Estado observado: branch `cursor/fix-governance-gaps-ec54`, commit `3aa4ebb`. Gate Agregador do PR passou na run `38690629942`. Este documento não autoriza produção, não qualifica tarefa e não substitui Work Order.

Automático significa executar a próxima onda cujo gate esteja verde e parar no primeiro gate vermelho. Não significa promover, copiar ou apagar sem o procedimento qualificado.

## Autoridade

A escrita canônica entra por `python -m packages.cli.kernel`. Procedimentos qualificados hoje: `obter`, `atomizar`, `validar`, `retirar`, `registrar-find`, `vincular-find`, `analisar-find`, `corrigir-find`, `encerrar-find`.

T01, T02, T04 e T07 continuam não qualificadas. `ingest`, `process`, `pipeline run`, `registry add`, `registry set-status` e `scripts/migrar_drive.py` saem com código 2 antes de gravar.

O Git versiona código, contratos e governança. O corpus canônico não está homologado. O Supabase é destino previsto, não a autoridade atual. `authorized_by` continua texto.

## Onda 0 — já no checkout

Portas de escrita do CLI antigo fechadas. `FIND-0001` e `FIND-0002` abertos. 104.668 candidatos em `Não verificado`. 7.679 linhas em quarentena. 336 identificadores com textos diferentes, sem escolha de lado. 109 itens do Drive relidos como ausentes na lixeira recuperável. Quatro raízes do Drive com exclusão bloqueada.

## Onda 1 — listagem, sem cópia e sem lixeira

Fechar a listagem das pastas ainda abertas. Uma página de arquivos sem `nextPageToken` está completa. Uma página só com token, ou `{}`, não prova pasta vazia.

Pastas ainda sem lote: `revisao`, `atomizado`, `protocolos_enfermagem`, `suprimentos`, `raw`, `medicamentos`, `dispositivos`, `mesh`, `icd11`. Em `mesh` e `icd11` a listagem não fechou. Em `protocolos_enfermagem` o material é ato: sem extrator de dispositivo, a atomização falha fechada e nada vai para a lixeira.

Arquivos que permanecem no Drive nesta onda: `usda_sr_legacy_nutrientes.json` (87.096.800 bytes), o JSON Anvisa de dispositivos (68.436.293 bytes) e o JSON CATMAT (51.223.636 bytes). Acima de cerca de 50 MB não entra no Git.

## Onda 2 — duplicidade por hash

Nome e tamanho iguais não são identidade. Conteúdo idêntico em caminhos diferentes é uma cópia, registrada uma vez. O mesmo nome com hashes diferentes não tem lado escolhido e não sai do Drive.

`atomizado` só entra em comparação arquivo a arquivo com as cópias já versionadas. A árvore COFEN tem 249 pares de mesmo nome e tamanho entre `FEDERAL/COFEN` e `NORMATIVOS/FEDERAL/COFEN`; os dois hashes precisam existir antes de qualquer descarte. Os 336 conflitos do legado continuam sem fusão.

## Onda 3 — lote de referência

Só começa com listagem fechada e todo arquivo abaixo de cerca de 50 MB. Cada lote usa quatro Work Orders, nesta ordem: `obter`, `atomizar`, `validar`, `retirar`.

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
4. Arquivo com cerca de 50 MB ou mais.
5. Licença desconhecida, ou cópia que exigiria alteração de ICD-11.
6. Tarefa fora dos nove procedimentos qualificados.
7. Work Order inválida, ou `FIND` crítico aberto quando o passo promove status.
8. Gate Agregador do PR em falha.
9. Tentativa de esvaziar lixeira, aplicar migration, ativar proteção de branch ou declarar `FOUNDATION_COMPLETE` por código.

Proteção da `main`, aplicação da migration, esvaziamento da lixeira e assinatura institucional de `authorized_by` continuam humanas. Identity Issuer e Master Registry continuam não comprovados. As listas de estado de `docs/REGISTRY.md` e de `packages/cli/registry.py` não são unificadas por este plano.
