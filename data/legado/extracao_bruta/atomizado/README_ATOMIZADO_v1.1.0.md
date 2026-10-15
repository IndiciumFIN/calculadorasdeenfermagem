# Biblioteca atomizada (fases 1 e 2) — README v1.1.0

Gerada por `atomizar.py` (versão 1.1.0; no Drive: `atomizar_v1.1.0.py`) a partir dos CSV/JSON limpos de `/workspace/doencas/<tema>/`. Verificada por `verificar.py` (1.1.0; no Drive: `verificar_v1.1.0.py`). As versões 1.0.0 (`atomizar.py`, `verificar.py`, `README_ATOMIZADO.md`) continuam no Drive, sem alteração.
Fase 1 = 8 temas únicos (cid10, icd11, medlineplus, dispositivos, medicamentos, nutricao, suprimentos, epidemiologico).
Fase 2 = 7 temas sobrepostos (sepse, sinais_vitais, vacinas, vacinal_brasil, ferimentos, protocolos_enfermagem, mesh).

**Fase 1 inalterada:** com a v1.1.0, a saída dos 8 temas da fase 1 é byte a byte idêntica à da v1.0.0 (verificado com `diff -r`). Por isso o `MANIFESTO.json` desses temas continua com `versao_gerador = "atomizar.py 1.0.0"`: esse campo registra a versão que define as regras do tema. Os temas da fase 2 registram "atomizar.py 1.1.0".

- Regerar: `python3 atomizar.py --entrada /workspace/doencas --saida /workspace/doencas_atomizado [tema ...]`
- Verificar: `python3 verificar.py /workspace/doencas_atomizado`
- Cada pasta de tema tem um JSONL por `tipo_entidade` (dividido em `.parte-NNNN.jsonl` quando passa de 90.000.000 bytes) e um `MANIFESTO.json`.
  O manifesto traz as contagens, o sha256 de cada arquivo, as fontes, o sha256 das entradas e a conferência com os CSVs, explicando cada diferença.

## Campos de cada átomo
`atom_id` (= `<tema>:<codigo>`), `tema`, `tipo_entidade`, `codigo`, `titulo`, `sinonimos`, `descricao_literal`, `fonte_nome`, `fonte_url`,
`fonte_versao`, `data_extracao`, `referencias_cruzadas` (`cid10`, `cid11`, `mesh`, `medlineplus`), `sha256`.

## Decisões
- **codigo**: é a chave local do átomo. Quando o tema tem mais de uma fonte ou mais de um tipo de entidade, leva um prefixo:
  - cid10: `cap:01`, `grupo:A00-A09`, `cido:M8000/0`, `cidogrupo:M800-M800`; categorias e subcategorias ficam sem prefixo (`A00`, `A00.0`).
  - icd11: `cap:01`, `bloco:<id numérico da entidade na linearização da OMS>`; categorias ficam sem prefixo (`1A00`).
  - medlineplus: `en:<id>` e `es:<id>`.
  - dispositivos e suprimentos: `anvisa:`, `fda:`, `catmat:`.
  - medicamentos: `anvisa:`, `anvisa-sem-registro:<hash>`, `cmed:<código GGREM>`, `fda-ndc:`, `fda-desabastecimento:`.
  - nutricao: `taco:`, `pof:<alimento>-<preparação>-<medida>`, `usda:<fdc_id>`.
  - epidemiologico: `notificacao-compulsoria:<nº><letra>`, `sim:<contador>`, `srag:<nu_notific>`.
    SINAN, mpox e febre amarela não têm id na fonte. Nesses casos o código são os 16 primeiros hex do SHA-256 do registro canônico; linhas idênticas recebem sufixo `-2`, `-3`… para não perder registros.
- **descricao_literal**: renderização literal (`campo: valor`, na ordem da fonte, sem os campos vazios) de todos os registros de origem da entidade. Nada é resumido.
  Quando uma entidade junta vários registros, eles vêm em blocos ordenados pelo JSON canônico. Tabelas-filhas (nutrientes USDA, ácidos graxos e aminoácidos TACO) aparecem como `## <arquivo>`, com uma linha por registro.
- **referencias_cruzadas**: as 4 chaves estão sempre presentes. Só são preenchidas por regra determinística:
  - MedlinePlus: os descritores MeSH do campo `mesh` e o átomo do tópico no outro idioma.
  - SINAN (`id_agravo`) e SIM (`causabas`): o código CID-10, só quando ele existe na tabela CID-10 da biblioteca (sem chute).
- **data_extracao**: 2026-10-10 para todas as fontes (data do download), fixa no script.
- **sha256**: calculado sobre o JSON canônico do átomo, sem o próprio campo sha256.


## Fase 2 (v1.1.0): decisões
- **Matriz de sobreposição**: `MATRIZ_CRUZAMENTO_NORMATIVOS_DADOS_2026-10-10.csv` (Drive id 1eJETouIY0YwoZ0qUg-ObYRmPLeKgcEy_, sha256 72968b5d…; cópia local em `_entradas/`). Ela tem 98 linhas: 83 de normativos (Cofen etc.) e 15 linhas `TEMA|<tema>` sobre os dados.
  - Cada MANIFESTO da fase 2 traz `sobreposicao_matriz` com: a linha literal do tema, as decisões tomadas, os mapeamentos item a item para Calculadoras-de-Enfermagem e os conflitos ou ambiguidades.
  - **Nenhum átomo foi removido por sobreposição**: a matriz não manda remover nenhum.
  - **Mapeamento item a item** só quando é determinístico: a linha da matriz cita literalmente o arquivo de origem do átomo e o prefixo de sha256 dela confere com o arquivo local.
    O único caso é `RES|736|2024` → `protocolos_enfermagem:protocolo:resolucao-cofen-no-736-2024-processo-de-enfermagem` (prefixo 3fb4e597, confere).
    Ele aponta para a pasta canônica `Calculadoras-de-Enfermagem/cofen/BR_FED_COFEN_RES_2024_N_00736`.
  - As outras linhas são só no nível do tema (a matriz não lista itens).
  - `referencias_cruzadas` continua com as 4 chaves exatas do spec. A ligação com Calculadoras-de-Enfermagem fica no MANIFESTO; não foi criada chave nova no átomo.
  - Os MANIFESTOs da fase 1 não foram alterados (para manter os bytes). As linhas TEMA da matriz para esses temas dizem "Canônica: A", sem sobreposição, exceto medicamentos ("escopos distintos").
- **Recortes** (sepse e ferimentos: cid10, cid11, mesh, medlineplus): são registros idênticos aos dos temas canônicos (conferido registro a registro). Ficam como átomos do tema, com tipo `recorte_<vocabulário>` e código `cid10:<código>`, `cid11:<código>` (ou `cid11:bloco:<id>`), `mesh:<UI>`, `medlineplus:<en|es>:<id>`.
  - `referencias_cruzadas` aponta para o átomo canônico:
    - cid10 = código;
    - cid11 = código (vazio nos blocos sem código);
    - mesh = UI;
    - medlineplus = atom_id do tópico e do outro idioma.
  - O `verificar.py` confere que toda referência existe como átomo.
- **Transcrições manuais** (Sepsis-3/SOFA/qSOFA, NEWS2, PA DBHA 2020) levam a marca em 4 lugares, conferidos pelo `verificar.py`:
  1. `tipo_entidade` termina em `_transcrito_manualmente` / `_transcrita_manualmente`;
  2. `fonte_nome` começa com `[TRANSCRITO MANUALMENTE]`;
  3. `fonte_versao` diz "transcrição manual digitada pelo Grok Bot em 2026-10-10 … não é extração automática";
  4. `descricao_literal` termina com a seção `## aviso (...)` copiada do arquivo.
  - `fonte_url` é o DOI/URL da publicação citada: SOFA → doi:10.1007/BF01709751; definições e qSOFA → doi:10.1001/jama.2016.0287; NEWS2 → página do RCP; PA → doi:10.36660/abc.20201238.
  - Os JSON aninhados transcritos (sem CSV) só geram átomos para o que não está nos CSVs: 2 definições + 2 descrições de escore (sepse) e 4 faixas de risco NEWS2 (sinais_vitais). O resto já vem dos CSVs.
- **PDFs de protocolos**: 1 átomo por documento do índice (12, incluindo os 2 da OMS cujo download falhou). `descricao_literal` = registro literal do índice; `fonte_url` = URL oficial do documento.
  - O texto dos PDFs **não** foi extraído: depende da ferramenta e da versão, então não é trivialmente determinístico.
  - O sha256 e o tamanho de cada PDF local estão em `pdfs_locais` no MANIFESTO.
- **Códigos sem id na fonte**:
  - Chave natural literal em slug (minúsculas ASCII; `<=`/`>=`/`<`/`>` viram `le`/`ge`/`lt`/`gt`): SOFA/qSOFA, NEWS2, PA, CDSi, PCDT, índice de protocolos, nomes técnicos/PDM. Se dois nomes literais diferentes dão o mesmo slug (ex.: `CURATIVO` e `CURATIVO.`), os dois recebem sufixo com 8 hex do SHA-256 do nome.
  - Sem chave natural única: 16 hex do SHA-256 do registro canônico (+ `-2`, `-3` para linhas idênticas). Vale para SIES (amostra), SESAI (ano+uf+dsei+polo se repete 1 vez) e Conitec tecnologias COVID-19.
  - Com id na fonte: PNI = `codigo_documento`; ESAVI = `numero_notificacao`; CVX = `cvx`; CDSi observações = `codigo`; MeSH = UI.
- **MeSH**: 1 átomo por descritor (31.110). `mesh_doencas_categoria_C` é subconjunto idêntico, então não gera átomos. `referencias_cruzadas.medlineplus` = tópicos MedlinePlus que citam o descritor no campo `mesh` (regra reversa).
- **Não atomizados** (arquivos brutos em `raw/`): perfis FHIR e value set (incluem 8478-0, PA média, que não está no CSV limpo), zips CDSi (dois downloads iguais), respostas brutas da API do MS, desc2026.gz.

## Resumo — fase 1 (versao_gerador 1.0.0)
| Tema | Átomos | Arquivos | Por tipo_entidade |
|---|---|---|---|
| cid10 | 15,407 | 6 | capitulo (22), categoria (2,045), cido_categoria (816), cido_grupo (61), grupo (275), subcategoria (12,188) |
| dispositivos | 107,792 | 3 | classificacao_fda_dispositivo (7,094), registro_anvisa_produto_saude (100,698) |
| epidemiologico | 31,631 | 9 | agravo_notificacao_compulsoria (81), caso_febre_amarela_humano_primata (2,913), epizootia_febre_amarela (2,637), notificacao_mpox (5,000), notificacao_sinan_chikungunya (3,000), notificacao_sinan_dengue (5,000), notificacao_sinan_zika (3,000), notificacao_srag (5,000), obito_sim (5,000) |
| icd11 | 37,052 | 3 | bloco (1,360), capitulo (28), categoria (35,664) |
| medicamentos | 204,308 | 6 | apresentacao_cmed (26,635), desabastecimento_fda (1,552), produto_anvisa_sem_numero_registro (7,430), produto_fda_ndc (135,893), registro_anvisa_medicamento (32,798) |
| medlineplus | 2,033 | 2 | topico_saude_en (1,017), topico_saude_es (1,016) |
| nutricao | 20,586 | 4 | alimento_taco (597), alimento_usda_foundation (395), alimento_usda_sr_legacy (7,793), medida_caseira_pof (11,801) |
| suprimentos | 79,369 | 4 | classificacao_fda_seringa_agulha_luva_curativo (157), item_catmat (59,938), item_catmat_seringa_agulha_luva_curativo (10,493), registro_anvisa_seringa_agulha_luva_curativo (8,781) |

## Resumo — fase 2 (versao_gerador 1.1.0)
| Tema | Átomos | Arquivos | Por tipo_entidade |
|---|---|---|---|
| ferimentos | 1,607 | 5 | nome_tecnico_anvisa_curativo (3), pdm_catmat_classe_6510 (73), recorte_cid10 (481), recorte_cid11 (742), recorte_mesh (308) |
| mesh | 31,110 | 1 | descritor_mesh (31,110) |
| protocolos_enfermagem | 105 | 3 | documento_protocolo (12), pcdt_conitec_situacao (83), tecnologia_diretriz_covid19_conitec (10) |
| sepse | 108 | 7 | criterio_escore_transcrito_manualmente (33), definicao_transcrita_manualmente (2), escore_transcrito_manualmente (2), recorte_cid10 (35), recorte_cid11 (22), recorte_medlineplus (6), recorte_mesh (8) |
| sinais_vitais | 58 | 4 | classificacao_pa_dbha2020_transcrita_manualmente (6), codigo_loinc_perfil_fhir (12), pontuacao_news2_transcrita_manualmente (36), risco_news2_transcrito_manualmente (4) |
| vacinal_brasil | 15,377 | 4 | cobertura_vacinal_polo_sesai (377), dose_aplicada_pni (5,000), movimento_insumo_sies (5,000), notificacao_esavi (5,000) |
| vacinas | 1,365 | 4 | associacao_cvx_antigeno_cdsi (291), codigo_cvx (290), dose_esquema_cdsi_acip (506), observacao_condicao_cdsi (278) |
