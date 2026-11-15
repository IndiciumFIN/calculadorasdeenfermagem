# Avaliação canônica de extensões, widgets e demais canais · v1.3.0

Status: **planejamento candidato / não implementado / não homologado**. Anexo incremental às matrizes v1.1.0 e v1.2.0. Data: 2026-11-15.

## 1. Decisão de arquitetura

**Um núcleo canônico + várias projeções, sem duplicar fontes de verdade.** Usar `Capability/Tool/Content/Service Registry`, `UserState (favorites, read-later, collection, recent, progress)`, `WorkspaceLayout`, `Notifications`, `OfflinePackage`, `Version`, `Entitlement`, `Evidence`, `Source/License` e contratos de UI. Cada canal publica somente capacidades com autorização e suporte real, usando o mesmo `canonical_id` e endpoints controlados. Não recriar tabelas de favoritos por canal; preferências e layouts têm *namespaces* por usuário e superfície. O DS determina tokens e componentes, não regras clínicas.

## 2. Extensão Chrome/Edge: proposta funcional para a primeira wave

**Páginas da extensão:** popup/launcher (busca + favoritos + acesso), Side Panel (tela principal), opções/preferências (temas, idiomas, consentimento, ocultar dados), área offline (status de versão e download), login via fluxo autorizado, importação de links, coleções e história de sincronização. O histórico de navegação geral não deve ser coletado. A interface do painel lateral deve compartilhar tokens e primitives com o site sem carregar seu DOM indiscriminadamente.

**Controles:** abrir no site, abrir painel, salvar favorito, ler mais tarde, adicionar à coleção, copiar referência, gerar citação autorizada, pesquisar, filtrar, ordenar, remover, sincronizar, reprocessar falhas, ver fonte e última atualização, reportar problema, sair. Estado: convidado, autenticado, acesso negado, online, offline, expirado, sincronizando, erro de API, conflito, cache desatualizado. Favoritos públicos podem operar localmente sem autenticação; a sincronização exige login e tratamento de conflitos.

**Manifest V3:** permissões estritamente necessárias (`storage`, `sidePanel`, `contextMenus` se ativado); `activeTab` apenas em gesto explícito; `host_permissions` limitadas ao domínio próprio; evitar `<all_urls>`, `webRequest` indiscriminado, gravação de formulários e scraping invisível; scripts embarcados; CSP e validação de mensagens. `background.service_worker` não mantém timers contínuos: usar `alarms` para lembretes pessoais sujeitos à plataforma. Sem prometer alarmes clínicos críticos ou execução sempre ativa. Confirmar requisitos atualizados da loja antes da submissão. A política Chrome exige um propósito único claramente descrito e tratamento limitado de dados (a suíte ampla será representada como *assistente de acesso e organização*, sem finalidades desconexas).

**Portabilidade:** Edge (Chromium) compartilha grande parte das APIs; Firefox exige adaptador de `sidebar_action` e compatibilidade de permissões. Safari exige análise distinta de empacotamento e distribuição. Não prometer mesmo comportamento em todas.

## 3. Widgets

- **Internos:** tarjetas de próximos plantões, relógio/cronômetro pessoal, agenda, calculadora favorita, recentes, progresso de trilha, concursos novos, checklist pessoal, PDI, Kanban, artigos salvos, caixa de notificações. Cada widget deve ter `widget_type_id`, `view_contract_id`, `canonical_object_ref`, capacidades permitidas, tamanho responsivo, versão, gatilhos de atualização, política de cache e acessibilidade.
- **Externos embutíveis:** calculadora pública validada, quiz e concursos. Distribuição por `<iframe sandbox>` com `postMessage` de origem verificada e CSP, sem dados pessoais ou assistenciais; registro de parceiro, quota, versão, fontes e política de revogação.
- **Homescreen Android/iOS:** widgets *nativos* exigem apps/empacotamento específico. Uma PWA, por si só, não garante widgets equivalentes no launcher do sistema; limites de atualização são impostos pelo SO.
- **Microações:** favoritar, concluir, abrir no app, alternar período e copiar link. *Drag-and-drop* com alternativa via teclado/menu e WCAG 2.2; animação com `prefers-reduced-motion` e feedback de estado.

## 4. Recursos adicionais sugeridos

1. Launchers de ferramentas e atalhos por especialidade; busca de comandos com teclado; central de itens fixados.
2. Captura de fontes com provenance/licença, sumário pessoal, marcação e fila de leitura.
3. Widgets agregadores de plantão, calendário, tarefas e estudos; modelos de workspace.
4. Share target, shortcuts/quick actions e links profundos em web e nativos.
5. Modo de consulta pública offline com conteúdo versionado e aviso de validade; **sem paciente identificado**.
6. Compartilhamento de widget de site parceiro (público, com controle de origem).
7. Modo noturno/alto contraste, fontes grandes, controle por teclado, suporte a leitores de tela.
8. Integração com Google/Apple/Outlook Calendar por opt-in; exportação ICS com granularidade de privacidade.
9. Relatórios de falhas de sincronização, botão Retentar e últimos checkpoints auditáveis.
10. Planos de acesso (upsell/downsell) sempre resolvidos por autoridade do servidor; extensões mostram apenas a oferta e direitos atuais.

## 5. Proibições e HOLD

- Não capturar tela, EHR/prontuário, notas clínicas, login, tokens nem páginas de terceiros automaticamente.
- Não coletar ou compartilhar dados de pacientes em Chrome sync, armazenamento de extensão, widgets na tela bloqueada, calendário de família ou redes sociais.
- Não implementar alarmes/monitoramento clínico como simples notificação web. Avaliar função pretendida, uso institucional, requisitos Anvisa e testes de segurança.
- Não tratar PWA e WebExtension como serviços always-on: service workers são interrompíveis; reentrância e idempotência obrigatórias.
- Não ativar upload/telemetria sem consentimento adequado e finalidade definida.
- Integrações EHR/FHIR, Teams corporativo e LMS acadêmico ficam condicionadas a contratos, autorização e especificação institucional.

## 6. Evidência e URLs oficiais consultadas

- Chrome Side Panel API: https://developer.chrome.com/docs/extensions/reference/api/sidePanel
- Chrome Manifest V3 / worker lifecycle: https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle
- Chrome declare permissions: https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions
- Chrome Web Store limited use: https://developer.chrome.com/docs/webstore/program-policies/limited-use
- Chrome Web Store policies: https://developer.chrome.com/docs/webstore/program-policies/policies
- MDN WebExtensions compatibility: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Chrome_incompatibilities
- MDN PWA offline/background sync: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Offline_and_background_operation
- Android widgets: https://developer.android.com/develop/ui/views/appwidgets/overview

## 7. Próximo gate

Inventário repo/branches → reconciliar propostas existentes → especificar contratos e estados → protótipo funcional Side Panel, Workspace Widget e Embed → testes com técnicos/enfermeiros e docentes → acessibilidade/segurança/offline → aprovar WO Kernel → implementação gradual. Esta entrega é documentação, **não publicação da extensão nem alteração do código**.
