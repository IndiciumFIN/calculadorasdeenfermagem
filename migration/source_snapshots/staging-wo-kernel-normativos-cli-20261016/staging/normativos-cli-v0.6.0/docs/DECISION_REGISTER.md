# Registro de decisões — pacote local

| ID | Decisão | Estado | Justificativa |
|---|---|---|---|
| DEC-01 | Executar 10 agentes determinísticos por Kernel local | APLICADA | WO por fase e evidência encadeada |
| DEC-02 | Reservar IDs `WO-LOCAL-*`, sem consumir sequências oficiais | APLICADA | Kernel oficial é autoridade de WOs oficiais |
| DEC-03 | Não executar o Kernel oficial nesta entrega | APLICADA | Validação ocorrerá após a finalização local |
| DEC-04 | Preservar integralmente os originais | APLICADA | Sem movimento, exclusão ou overwrite |
| DEC-05 | Não excluir pastas vazias automaticamente | APLICADA | Proposta de limpeza requer WO de exclusão e validação independente |
| DEC-06 | ZIPs suspeitos em HOLD sem extração | APLICADA | Limites, CRC, zip-slip, symlink, membros repetidos |
| DEC-07 | Não deduplicar nem descartar automaticamente | APLICADA | Comparação apenas gera candidatos |
| DEC-08 | Atomizar somente limites explícitos, sem inventar dispositivos | APLICADA | Textos editoriais geram HOLD |
| DEC-09 | Front-end: inspeção estática não equivale a renderização | APLICADA | `frontend=NOT_VERIFIED` |
| DEC-10 | Criar register por objeto e por norma candidata | APLICADA | Identidade normativa incerta separada em `objetos_sem_norma_identificada.csv` |
| DEC-11 | Submissão oficial exige WOs e validadores qualificados | PENDENTE | Revisão de políticas, testes e evidência independente |
