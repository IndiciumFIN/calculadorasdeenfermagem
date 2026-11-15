# UFCSPA — atomização de metadados da matriz de Enfermagem a partir de 2023 (W7 v0.5.6)

A página institucional da [UFCSPA](https://ufcspa.edu.br/vida-academica/graduacao/cursos/enfermagem/matriz-curricular), atualizada em **29/10/2025**, publica dez semestres da matriz de Bacharelado em Enfermagem vigente para ingressos a partir de 2023, com códigos, títulos e carga horária em horas-relógio.

## Resultado da leitura e preservação de inconsistências

| Indicador | Resultado |
|---|---:|
| Semestres | **10** |
| Ocorrências de disciplinas/grupos | **54** |
| Códigos distintos | **52** |
| Total semestral contado | **4.400 horas** |
| Optativas | 60h |
| Atividades complementares | 137h |
| **Total do bacharelado** | **4.597 horas** |
| Estágios incluídos nos semestres 9/10 | 920h |
| Códigos repetidos que precisam de tratamento específico | 2 |

### Duas diferenças importantes

**`XENF01001` — Seminário Integrador em Atenção Primária à Saúde:** aparece nos semestres 1 (Turma A) e 2 (Turma B). A nota da instituição estabelece que a carga horária de 60h é computada apenas no primeiro semestre, apesar de a atividade ocorrer em turmas distintas. Registro preservado em dois itens, **sem duplicação do total de 60h**.

**`ENF04004` — código com rótulos diferentes:** aparece no semestre 2 como "Fundamentos Teóricos da Enfermagem II" (30h) e no semestre 4 como "Fundamentos para Prática de Enfermagem II" (180h). Isso é **divergência da própria matriz pública**, não autorização para alterar código ou nome. A resolução exige ementa/versão ou retorno institucional; ambos continuam `HOLD_CODE_COLLISION`.

### Status de formação e autorização

As 54 ocorrências estão descritas em `UFCSPA_COMPONENTS_54_v0.5.6.jsonl` com instituição, edição, semestre, carga original e carga contabilizada, URL e sinalização de conflitos. **Não** são 54 átomos clínicos, competências certificadas, licenças ou microaulas prontas. Os códigos do bacharelado não constituem títulos de especialidade COFEN; níveis B/I/A serão avaliados após o exame de objetivos e pré-requisitos.

**QA:** 12/12 testes locais de consistência de horas e códigos aprovados. Nenhum texto integral de ementa, apostila, foto ou vídeo de terceiros foi reproduzido. `NO_GO_PUBLICATION`; sem inserção no Supabase ou merge na main.
