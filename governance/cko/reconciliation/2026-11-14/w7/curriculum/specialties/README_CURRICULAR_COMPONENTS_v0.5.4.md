# W7 v0.5.4 — extração dos componentes curriculares, sem confundir com evidência clínica

Nesta rodada foram registrados **120 componentes curriculares candidatos** de fontes públicas institucionais, sem reprodução de parágrafos completos de ementas ou conteúdos protegidos.

| Fonte | Componentes | Profundidade e limite |
|---|---:|---|
| USP EE, Bacharelado 2027 | 42 | Grade futura no Júpiter, códigos e semestres; ainda não é ementa clínica aprovada |
| USP EERP, Bacharelado 2027 | 8 | Amostra de disciplinas; **não é** extração integral |
| USP EE, Gestão de Serviços 2027–2028 | 8 | Módulos da página oficial, público multiprofissional |
| USP Apolo, Centro Cirúrgico e CME 2025–2027 | 3 | Objetivos editoriais condensados de atividade específica, não uma especialização independente |
| Faculdade Sírio-Libanês, Graduação 2027 | 41 | Unidades por nove semestres, início futuro em fevereiro/2027 |
| Sírio-Libanês Digital, Enfermagem Oncológica | 18 | Unidades curriculares sumarizadas, **sem turma/edição individual verificada** |
| Einstein: cursos existentes | 0 | Quatro páginas/catalogação confirmados; grade detalhada não extraída desta rodada |
| **Total** | **120** | **Candidatos curriculares, não átomos de evidência clínica** |

As matérias e seus semestres são preservados no JSONL `CURRICULAR_COMPONENT_DISCOVERY_120_v0.5.4.jsonl`; `source_program_id` relaciona cada registro à instituição e edição do catálogo v0.5.3. A carga horária total do curso pertence ao nível de programa e não deve ser atribuída individualmente a cada unidade quando ausente da fonte.

## O que falta para virarem conteúdo científico reutilizável

1. Confirmar ementa/objetivo, bibliografia, competências e pré-requisitos por edição e por disciplina.
2. Identificar o material científico/normativo correspondente, verificar licença e extrair afirmações atômicas rastreáveis.
3. Diferenciar regra normativa, interpretação pedagógica, cenário clínico fictício e evidência curricular institucional.
4. Relacionar o mesmo claim científico às disciplinas nas quais aparece, sem copiar a expressão protegida, sem confundir título de disciplina com homologação curricular.
5. Classificar nível básico/intermediário/avançado com rubrica e revisão humana; semestre isolado não é prova de dificuldade.
6. Produzir materiais autorais (artigos, aulas, simulados, cases, OSCE e checklists) com signoff editorial e clínico quando necessário.

**Resultado:** os 120 registros ajudam a mapear a grade e os pré-requisitos, mas **zero deles está autorizado automaticamente para publicação clínica**. Einstein continua `HOLD_CURRICULUM_GRADE`; USP e Sírio têm dados curriculares primários com direitos de republicação integral não demonstrados. Nenhuma alteração na `main` ou no Supabase.
