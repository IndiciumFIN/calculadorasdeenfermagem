# Evidências da voz da enfermagem: extensões de navegador, widgets e ferramentas rápidas · v1.3.1

**Data:** 2026-11-15 · **Status:** evidência candidata para pesquisa UX, não implementação / não homologação.

## Pergunta
Os enfermeiros preferem extensões do Chrome ou widgets? Quais funcionalidades demandam diretamente?

## Resposta fundamentada
Não há, entre as fontes identificadas nesta pesquisa, levantamento representativo de preferência por extensões Chrome entre enfermeiros. Há pedidos explícitos por widgets de escala e agenda, estudos qualitativos que apoiam acesso rápido, interfaces consistentes, menos cliques e melhor integração, e objeções ao acesso não autorizado a prontuários por extensões. Não converter necessidades de fluxo em estatísticas de preferência por canal.

## Evidências

| ID | Evidência | População / método | Achado relevante | Força e limitação |
|---|---|---|---|---|
| EVP-001 | NurseGrid App Store | Avaliações espontâneas | Usuários pedem widget de calendário na tela inicial, dark mode, comparação de colegas e cancelamentos visíveis | Direta para widget; auto-seleção, não representativa |
| EVP-002 | NurseGrid WorldsApps | Avaliações espontâneas, incluindo 2026 | Usuário pede widget para consultar escala sem abrir app | Direta para widget; origem agregadora |
| EVP-003 | JMIR Nursing 2025, EHR | Grupos focais com enfermeiros | Demandas por modelos consistentes, gestão de tarefas e mensagens seguras | Direta para fluxo, não para extensão |
| EVP-004 | CIN 2024 systematic review | 21 estudos de usabilidade EHR | Problemas de usabilidade elevam carga e contornos inseguros | Revisão, não preferência por Chrome |
| EVP-005 | Estudo 2025 sobre recursos clínicos no EHR | Entrevistas de 10 profissionais de saúde, com enfermagem | Preferências divergentes entre consulta integrada e janela separada | Pequena amostra multiprofissional |
| EVP-006 | BMC Nursing 2026 fadiga de alertas | Entrevistas com enfermeiros | Alertas excessivos causam sobrecarga e dessensibilização | Não determina tipo de app |
| EVP-007 | Reddit nursingjobs 2026 | Discussão espontânea com suspeita de promoção | Preocupação com extensão não aprovada que automatiza registros OASIS | Anedota de baixa confiabilidade, não adoção |
| EVP-008 | Sciencedirect 2025, 146 enfermeiros | Survey aberto de EHR | 56% mencionaram melhoras da interface; 17% documentação redundante | Responde desenho do fluxo, não do canal |
| EVP-009 | JMIR 2026 sobre turnos | Avaliação de app com trabalhadores por turnos | Controles e navegação de calendário precisam funcionar com uma mão | Indireta para widgets/extensões |

### Referências consultadas
- https://apps.apple.com/us/app/nursegrid-nurse-shift-calendar/id949731866?see-all=reviews
- https://worldsapps.com/reviews-nursegrid-nurse-shift-calendar
- https://nursing.jmir.org/2025/1/e69651
- https://pubmed.ncbi.nlm.nih.gov/38191474/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12149773/
- https://link.springer.com/article/10.1186/s12912-026-04592-1
- https://www.reddit.com/r/nursingjobs/comments/1wr6oku/charting_no_life/
- https://www.sciencedirect.com/science/article/pii/S0029655425001162
- https://formative.jmir.org/2026/1/e103689

## Decisão por canal (candidata)
1. Widget de agenda/plantões: **P0, prototipar e testar**. Acesso de relance, dark mode, comparador de escalas e cancelamentos. Sem dados assistenciais em tela bloqueada.
2. PWA / web responsiva: **P0, base de acesso**. Consulta rápida e offline versionado quando autorizado.
3. Extensão Chrome/Edge Side Panel: **P1, experimento controlado**, sem preferência de mercado comprovada; começar com busca, favoritos, ler depois, copiar referência e links, não ler automaticamente abas clínicas.
4. Widget de calculadoras: **P1, pesquisa com usuários**. Mostrar fontes e revisão; validar em tarefas reais.
5. Escrita automática no EHR por extensão: **HOLD** por risco regulatório, autorização e segurança de paciente.
6. Alertas por extensão: **P2 para lembretes pessoais opt-in**; não simular sistema de alarme clínico.

## Pesquisa de validação proposta
Recrutar, de maneira intencional, enfermeiros assistenciais, técnicos e estudantes, em serviços com diferentes níveis de informatização. Comparar três protótipos com as mesmas tarefas: (A) PWA, (B) painel lateral Chrome, (C) widget/atalho. Tarefas: localizar escala de amanhã, reencontrar calculadora validada, salvar referência, retomar estudo. Registrar taxa de conclusão, tempo, erros, cliques, SUS/SEQ, NASA-TLX quando pertinente, desistência, preferência declarada **após a tarefa**, fricções de instalação, permissão e privacidade. Não combinar resultados em rankings sem amostra suficiente e desenho pré-especificado.

## Critérios de governança
Proveniência por fonte, snapshot/version, classificação de qualidade, nenhum acesso a dados de pacientes, aplicações aprovadas pela instituição, DPO/LGPD, consentimento, falhas offline, WCAG 2.2 e telemetria minimizada. Kernel e WO validada antes de alterar código governado. **Este adendo não declara nenhuma ferramenta como implementada**.
