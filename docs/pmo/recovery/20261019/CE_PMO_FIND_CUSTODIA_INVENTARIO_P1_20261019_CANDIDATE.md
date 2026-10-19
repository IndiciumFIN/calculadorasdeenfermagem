# CE PMO — Microlote P1-A: inventário recursivo e custódia

Status: `EVIDENCE_CAPTURED_CANDIDATE`; gate PMO permanece `HOLD`.

## Baseline e escopo

- Branch documental autorizada: `pmo/recovery-controlled-20261019`; nenhum merge ou limpeza destrutiva.
- Escopo: somente arquivos regulares no workspace local atual. O coletor não acessa Drive, Supabase ou branches remotas.
- Instrumento: `ce_pmo_inventory_recursive_v02.py --no-write` (execução observada com exit code 0).
- Resultado agregado público: `CE_PMO_INVENTARIO_RECURSIVO_RESUMO_20261019_CANDIDATE.json`.
- O manifesto com caminhos individuais e SHA256 é **privado** por conter nomes de uploads; sua publicação exige triagem de direitos, segredos e dados pessoais.

## FINDs e ações corretivas

| FIND | Constatação | Correção aplicada / situação | Gate |
|---|---|---|---|
| PMO-FIND-P1-001 | Inventário anterior com 145 arquivos era seletivo, sem pastas profundas. | Criado scanner recursivo, relatório por grupo, SHA256 e duplicidades por hash. | HOLD: ainda falta confronto externo |
| PMO-FIND-P1-002 | `LIBRARY_VERSION_1_CONFIRMED` era inferido pelo nome de um ZIP, não por readback. | Removida inferência do coletor antigo; novo usa `NOT_PROVEN_BY_LOCAL_SCAN`. | HOLD: prova externa separada |
| PMO-FIND-P1-003 | Relatório antigo podia ser truncado em falha de escrita. | Escrita atômica via arquivo temporário + fsync + replace em ambos coletores. | PARTIAL: teste de falha injetada pendente |
| PMO-FIND-P1-004 | Listar conteúdo de ZIP não garante integridade de payload. | Inventário de diretório central por ZIP, marcado explicitamente como não verificado integralmente. | HOLD: extração segura/check CRC pendentes |
| PMO-FIND-P1-005 | Há symlinks e dependências no workspace que não são automaticamente documentos-fonte. | Symlinks são contados e não seguidos; diretórios são estratificados. | HOLD: classificação documental pendente |

## Medições desta execução

- **768 arquivos regulares**, **40.897.025 bytes** e **720 SHA256 únicos**.
- **23 grupos de duplicidade exata**, incluindo **71 caminhos**; isto **não** autoriza exclusão.
- **13 arquivos ZIP** com **1.956 entradas regulares declaradas**; **0** diretórios centrais ilegíveis nesta passagem.
- **776 symlinks ignorados**, sem perseguição de links.
- Grupos: raiz 153; uploads 22; `admin_project_review` 247; `cko_val_001` 338; helpers 5; demais aninhados 3.
- Os números representam um **snapshot local**, não a população definitiva do projeto. Arquivos de relatório gerados são excluídos da população para evitar autorreferência.

## Testes e limites

- PASS: execução `--no-write`, exit 0; leitura de central directory de 13 ZIPs; SHA256 de cada arquivo regular; estratificação.
- HOLD: manifesto privado durável, auditoria de integridade dos payloads ZIP, teste negativo de escrita, reconciliação GitHub/Library/Supabase, evidência de autorização e homologação.
- Não inferir completude global nem declarar PMO aprovado por estes resultados.

## Próximo microlote

1. Executar testes negativos e reexecução idempotente do coletor.
2. Classificar duplicidades e separar dependências de fontes do corpus.
3. Confrontar ZIPs/manifestos com custódia externa **sem publicar nomes confidenciais**.
4. Atualizar Registro Mestre com controle de evidências e deixar gates `HOLD` até auditoria independente.
