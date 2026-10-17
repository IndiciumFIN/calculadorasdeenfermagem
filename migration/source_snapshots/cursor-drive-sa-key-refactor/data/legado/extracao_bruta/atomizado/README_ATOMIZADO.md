# Biblioteca atomizada (fase 1)

Gerada por `atomizar.py` (versão 1.0.0) a partir dos CSV/JSON limpos de `/workspace/doencas/<tema>/`. Verificada por `verificar.py`.
São os 8 temas únicos. Os temas sobrepostos (sepse, sinais_vitais, vacinas, vacinal_brasil, ferimentos, protocolos_enfermagem e mesh) ficam para a fase 2.

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

## Resumo
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
