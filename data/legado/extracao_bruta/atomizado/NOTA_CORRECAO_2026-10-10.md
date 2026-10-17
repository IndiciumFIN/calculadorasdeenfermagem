# Correções de 10/10/2026 (sepse e sinais_vitais), versão v2

Nenhum arquivo da versão 1 foi editado, apagado ou sobrescrito. As versões novas são arquivos à parte.

## O que mudou
1. **Choque séptico (sepse:definicao:choque-septico)**
   - Entrou "hipotensão persistente", como está no Sepsis-3, Box 3 (JAMA 2016;315(8) p.805): "...persisting hypotension requiring vasopressors to maintain MAP ≥65 mm Hg...".
   - O trecho literal em inglês foi incluído no átomo.
   - Entrada nova: `doencas/sepse/criterios_sepsis3_v2.json`.
2. **Classificação da PA, DBHA 2020 (6 átomos sinais_vitais:pa-dbha2020:\*)**
   - Entraram, literalmente, as notas *, ** e *** do Quadro 3.4 (Arq Bras Cardiol 2021;116(3) p.545).
   - Entradas novas: `classificacao_pressao_arterial_dbha2020_transcrita_v2.json` e `.csv`, e `referencias_sinais_vitais_transcritas_v2.json`.
   - `criterios_sofa_qsofa` não mudou, então não há v2 dele.

## Arquivos novos
- `atomizar_v1.2.0.py`: só gera sepse e sinais_vitais e só escreve em pasta de staging.
- `sepse/definicao_transcrita_manualmente_v2.jsonl` e `sepse/MANIFESTO_v2.json`.
- `sinais_vitais/classificacao_pa_dbha2020_transcrita_manualmente_v2.jsonl` e `sinais_vitais/MANIFESTO_v2.json`.
- `sepse/MANIFESTO_2026-10-10.json` e `sinais_vitais/MANIFESTO_2026-10-10.json`: pendências PENDENTE_REVISAO_HUMANA de antes da correção.

O MANIFESTO_v2 aponta para os arquivos `_v2` que mudaram. Os que não mudaram continuam com o nome original (bytes idênticos).

## Regras mantidas
- Os atom_id são os mesmos (mesma entidade). Os sha256 foram recalculados.
- A marca [TRANSCRITO MANUALMENTE] foi mantida.
- O fonte_versao ganhou "; corrigido a partir da fonte em 2026-10-10 (...)".
- Os cabeçalhos "## aviso (...)" continuam citando o nome do arquivo de origem do aviso. O texto do aviso não mudou, por isso os átomos que não mudaram ficaram byte a byte iguais.

## Verificação
- Duas execuções do gerador deram saída byte a byte idêntica.
- `verificar.py` 1.1.0 rodou duas vezes sobre a árvore completa com as v2 no lugar. Saída idêntica e TUDO OK: sepse 108 átomos, sinais_vitais 58, sem atom_id duplicado, fonte_url preenchida, contagens conferem.
- A árvore v1 oficial continua TUDO OK.

## Situação da revisão humana
- Corrigidos (o texto agora confere com a fonte):
  - choque séptico: 1 linha da revisão;
  - notas do Quadro 3.4: 1 linha da revisão, 6 átomos.
- Continuam PENDENTE_REVISAO_HUMANA as **3** linhas não localizadas, todas em sepse:
  - SOFA "total 0-24";
  - SOFA "fonte Vincent 1996" (original não acessível);
  - qSOFA "1 ponto por item".
- O relatório anterior falava em "4 não localizadas / 115 linhas". O certo é 3 não localizadas / 114 linhas.
