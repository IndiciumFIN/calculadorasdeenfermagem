# Aula integrada — centro cirúrgico → SRPA (sem fundir os objetos)

**Tipo:** aula transversal de documentação; **status:** CANDIDATE / HOLD_HUMAN / NO_GO.

## O percurso de informação

```text
Registro de recepção ao Centro Cirúrgico
   ├── PE / documentação de enfermagem (COFEN 736; W3)
   ├── verificações de segurança cirúrgica (RDC 36, MS e OMS)
   └── referências pertinentes a materiais (consulta técnica CME / W5)
                 ↓ transferência de contexto, não fusão de tabelas
Registro de recebimento na SRPA
   ├── observação documentada pela equipe responsável
   ├── evolução do PE segundo competência
   └── referências a avaliações/instrumentos *somente após validação*
```

As setas representam **correspondências pedagógicas** e não instruções de fluxo assistencial. Cada item possui autor, finalidade, controle de acesso e evidência próprios. O que é compartilhado pode ser representado por IDs e carimbos de tempo; não inserir fichas técnicas completas de processamento no prontuário nem duplicar informações pessoais desnecessárias.

## Tarefa de investigação para o aluno
Receba quatro documentos sintéticos: (1) anotação com horário; (2) checklist com campo em branco; (3) mensagem de passagem; (4) resultado exibido por simulador de Aldrete sem versão. Identifique a função de cada um, indique evidências que faltam e monte um quadro com quatro colunas: `afirmação`, `fonte`, `responsável`, `estado da verificação`. Não classifique como concluído o que não possui evidência. O escore sem fonte deve permanecer `HOLD`.

## Critérios de correção
O aluno deve: manter separação CC / SRPA / CME; distinguir checklist de PE; preservar autoria e cronologia; não inventar dados do paciente; não assumir critérios de alta; e apontar que os arquivos legados em espanhol, tailandês e neerlandês precisam ser reconciliados antes do uso em pt-BR.

## Referências ao corpus
- `CKO-W6-CC-EDUCATIONAL-COMPANION` → `CKO-W6-SRPA-EDUCATIONAL-COMPANION`: `CONTINUITY_EDUCATIONAL_CANDIDATE`.
- Ambos → `CKO-CORE-PROCESSO-ENFERMAGEM`: `CONTEXTUALIZES`, não `EQUIVALENT_TO`.
- SRPA → `W6-LEGACY-ALDRETE`: `MENTIONS_EXISTING_TOOL_REVIEW_REQUIRED`, sem equivalência a licença ou autorização clínica.
- CC → `W6-LEGACY-SAEP` / `W6-LEGACY-LVSC`: `HISTORICAL_ASSET_EVIDENCE`.
- CME → `CKO-W5-CME-FUNDAMENTOS-PROCESSAMENTO`: `CROSS_SPECIALTY_REFERENCE_ONLY`.
