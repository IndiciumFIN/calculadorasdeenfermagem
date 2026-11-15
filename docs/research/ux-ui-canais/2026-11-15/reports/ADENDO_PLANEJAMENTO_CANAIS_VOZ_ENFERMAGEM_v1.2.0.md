# Adendo UX/UI canônico — vozes da enfermagem, funcionalidades e canais — v1.2.0

**Natureza:** estudo documental/benchmark e novas capacidades candidatas; sem implementação, homologação, publicação ou migração. Complementa o planejamento v1.1.0 e não o substitui.

## Síntese

- 36 funcionalidades/capacidades candidatas, majoritariamente extensões de serviços já planejados.
- 24 canais/projeções avaliados. Não são 24 aplicativos a construir.
- 16 evidências/fontes categorizadas entre estudos, opinião setorial e relatos anedóticos.
- IDs locais UX-CAND-DELTA-* não substituem os IDs emitidos pelo Kernel. Antes de implementação, executar deduplicação com Registry e DS; nenhuma ação sem WO válida.

## Princípios de derivação

1. **Necessidade observada não é especificação aprovada**: feedback e pesquisa fornecem hipótese, a ser validada por testes de tarefas e entrevistas.
2. **Uma fonte canônica por objeto**: ContentRegistry/ToolRegistry + direitos/permissões + Experience/Channel Adapters. Fav/Progresso/Agenda/Tarefa são serviços compartilhados; não duplicar por canal.
3. **Canal ≠ produto**: WhatsApp/Instagram/YouTube são canais de distribuição/retorno; não mantêm estado clínico governado.
4. **Segurança clínica**: PWA pública = ferramentas referenciais validadas e conteúdo licenciado. Paciente, prontuário, alarmes de segurança e avaliação clínica automatizada exigem projeto institucional e avaliação regulatória separados.
5. **Mensageria**: preferências/opt-in, privacidade, limitação de dados e logs de entrega; sem PHI em notificações, widgets ou mídia social.

## Personas e canais por tarefa

| Persona | Tarefa primária | Canais primeiro | Evitar |
|---|---|---|---|
| Estudante | Revisar/treinar/acompanhar estágio | Web/PWA, YouTube, Instagram, LMS | App separada por disciplina |
| Enfermeiro assistencial | Consulta pontual, agenda pessoal, referências | Web/PWA, atalhos, offline validado | Marketing no modo de urgência, registro PHI em navegador público |
| Gestor | Escala, avaliação, treinamento, políticas | Desktop institucional, PWA, integração calendário | Publicação de escala por gesto sem aprovação |
| Preceptor/docente | Competências, feedback, trilhas, simulações | Web, LMS, app/PWA | Certificação sem evidência e autenticação |
| Enfermeiro pesquisador | Busca, fonte, bibliografia, projeto | Web desktop, extensão, exportação | Referência sem provenance/licença |
| Comunidade/público | Educação, busca e fórum moderado | Web, YouTube, Instagram | Misturar com sala clínica ou profissional |

## Canais — rollout candidato
P0 web público e workspace, PWA Android e iOS; P1 notificações opt-in, conteúdo audiovisual e calendário exportável; P2 nativo e integrações educacionais/widgets/extensão/assistente; P3 relógio/totem e conectores clínicos somente após evidência, consentimento e gates.

## Telas adicionais a especificar (candidatas, não contagem homologada)
Caixa de entrada universal; preferências de notificação; editor de padrão de escala; agenda multimodal; opção compartilhar disponibilidade; simulador de conflitos de jornada; comunicados institucionais; histórico de ciência; buscas por siglas; leitura de mudança em protocolo; diagnóstico de sincronização; revisão curta de flashcards; competência/preceptoria; resumo de pesquisa de satisfação; central de feedback de tarefa; conectores por canal; escopo de consentimento; comparação de planos transparente; estados de proteção de dados.

## Plano de pesquisa com usuários brasileiros (a executar; não é evidência já coletada)
1. Recrutar por papel, especialidade, turno e familiaridade digital: estudantes, técnicos, enfermeiros assistenciais, gestores, docentes/preceptores, APS e atenção domiciliar. Obter consentimento e evitar dados de pacientes.
2. Testar em dispositivos móveis de entrada e desktop, em redes estáveis e instáveis; tarefas: encontrar calculadora, salvar favorito, retomar simulado, criar escala pessoal, copiar plantão, saber estado sync e mudar plano.
3. Métricas: taxa de conclusão por tarefa, tempo, erros críticos, sucesso sem ajuda, SEQ, SUS/UMUX-Lite, uso de acessibilidade, fricção em 1 mão, confiabilidade da retomada.
4. Entrevistas breves depois das tarefas: qual ação ficou escondida, quais dados repetidos, o que é inviável no plantão, qual canal realmente seria usado, o que incomoda nas notificações.
5. Registrar achados como evidência A (observado), B (relatado) ou C (hipótese); decidir priorização após validação, sem usar números internacionais como demanda brasileira.

## Bloqueios e critérios de aceite
- Evidência de origem vinculada a cada hipótese e tela. Marcar requisitos com HOLD conforme riscos, não prometer funcionalidades não implementadas.
- Contratos para cada botão: ação, resposta, permissão, estados, modo offline, falha, confirmação e teste.
- Alternativa a arrastar, leitura acessível, foco e contraste AA, botões em alcance móvel, sem animação decorativa no modo clínico.
- Reversibilidade de ações pessoais, rollback, versionamento, filas e ACK, política de exclusão de dados, gestão de direitos comerciais sem upsell no cuidado.

## Fontes consultadas
- **Nurses technology usability US 2026** (Pesquisa quantitativa; n=752): EHR SUS 57.3, monitoramento remoto 74.4; falhas e integração. Limite: Não generalizar ao Brasil. https://pmc.ncbi.nlm.nih.gov/articles/PMC13367925/
- **Documentation burden 2026** (Survey institucional; n=133): 92% documentação importante; 88% sobretudo para conformidade. Limite: Amostra de um centro. https://pubmed.ncbi.nlm.nih.gov/42127286/
- **Charting path forward 2025** (Survey de 5 estados EUA; n=146): 56% UI e 17% redundância documental citadas. Limite: Baixa taxa de resposta. https://pubmed.ncbi.nlm.nih.gov/40580643/
- **Nurse preferences scheduling 2025** (Grupos focais Suíça; n=21): 85% justiça/participação; 76% flexibilidade/autonomia. Limite: Amostra pequena qualitativa. https://formative.jmir.org/2025/1/e67747
- **TESE serious game Brasil 2026** (Validação de aplicativo; n=33): SUS 87.5 estudantes; 92.5 especialistas (11). Limite: Mede usabilidade da solução, não efetividade duradoura. https://scielo.br/j/rgenf/a/cVsttxrPjW8WhMPndK3QRwQ/?lang=pt
- **Shift-work mHealth app 2026** (Estudo de viabilidade; n=não estabelecido): Notificações alinhadas a turnos, pesquisas 3-4 min, navegação com polegar. Limite: Escopo estudo específico de saúde ocupacional. https://pmc.ncbi.nlm.nih.gov/articles/PMC13626070/
- **Nurses social media Europe 2026** (Survey; n=158): WhatsApp diário 91.8%, Instagram 39.9%, YouTube 26.6%. Limite: Predomínio amostral Sigma; não representativo Brasil. https://doi.org/10.1097/CIN.0000000000001616
- **WhatsApp and nursing groups 2026** (Survey institucional; n=326): 98.8% grupo do setor, 80.4% satisfação. Limite: Uso não autoriza PHI/identificadores. https://www.nature.com/articles/s41599-026-08874-6
- **Brasil Cofen national survey 2026** (Comunicado levantamento; n=não estabelecido): Coleta 2026 incluiu canais e serviços digitais; resultados segmentados ausentes. Limite: Não inferir preferências nacionais. https://cofen.gov.br/cofen-finaliza-pesquisa-nacional-com-profissionais-de-enfermagem-2026/
- **Cochrane mobile informal use 2024** (Revisão qualitativa; n=não estabelecido): Mensageria informal útil e sujeita a riscos de governança. Limite: Mistura profissões e regiões. https://pmc.ncbi.nlm.nih.gov/articles/PMC11348462/
- **NurseGrid scheduling feedback** (Depoimentos públicos; n=não estabelecido): Calendário pessoal e do trabalho num mesmo lugar. Limite: Anecdótico, não survey. https://www.reddit.com/r/nursing/comments/1ivn6ya/similar_app_to_nursegrid/
- **Schedule Google feedback Feb 2026** (Depoimentos públicos; n=não estabelecido): Dor sincronizar escalas irregulares com calendários pessoais. Limite: Anecdótico. https://www.reddit.com/r/nursing/comments/1r8bibt/scheduling_in_google/
- **Communication threads Jan 2026** (Depoimentos públicos; n=não estabelecido): Fragmentação EMR papel mensagens. Limite: Anecdótico. https://www.reddit.com/r/nursing/comments/1qed5tn/anyone_else_feel_like_half_the_problems_on_your/
- **Undergraduate nursing social learning 2026** (Survey; n=458): Instagram e TikTok populares em educação nessa amostra. Limite: Não extrapolar para enfermeiros brasileiros. https://www.mdpi.com/2227-7102/16/4/627
- **Nurse personal smartphones evidence** (Scoping review; n=não estabelecido): Busca rápida de informações, comunicação; distração, privacidade e política institucional. Limite: Estudos anteriores a 2020. https://pubmed.ncbi.nlm.nih.gov/33242012/
- **Nurse AI trends survey 2025-26** (Pesquisa setorial; n=não estabelecido): 54% IA para eliminar tarefas desnecessárias; 50% documentação ou educação do paciente. Limite: Amostra e metodologia devem ser verificadas antes de inferir mercado. https://www.myamericannurse.com/2025-2026-trends-survey/
