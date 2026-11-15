# W7 v0.3.6 — revisão estrutural com fontes normativas

**Resultado técnico:** 12/12 pares avaliados com o registro original dos 1.055 microtópicos, a W7 com 985 itens curriculares e fontes normativas institucionais. **Nenhuma relação semântica aprovada automaticamente.**

## Decisão por tipo do destino

- **5/12 encerrados como proposta PART_OF incompatível com o tipo de destino:** objetivos/competências de programa não são unidades curriculares que contêm subtópicos. IDs: `W7-CUR-REV33-012`, `014`, `021`, `026`, `027`.
- **2/12 encerrados como proposta PART_OF sem hierarquia comprovada:** destinos são etiquetas candidatas de tema canônico, sem relação pai–filho estabelecida. IDs: `W7-CUR-REV33-013`, `022`.
- **5/12 preservados para comprovação de disciplina/ementa/edição:** `W7-CUR-REV33-003`, `006`, `007`, `009`, `020`. Dois contêm o termo do microtópico no título da disciplina (`006` Toxicologia ocupacional, `020` Trauma musculoesquelético), mas isso **não comprova ementa completa** ou cobertura do subtópico.

**A.C.Camargo:** O caderno de 472h especifica início em 09/05/2026, enquanto a página de 432h especifica início em 13/08/2026. São datas de oferta diferentes; a incompatibilidade de horas não é demonstrada dentro da mesma edição. A correlação do alvo `CURITEM-00967` com uma edição específica continua não verificada.

**Normativas independentes:** Portaria GM/MS 5.674/2024 (atualiza LDRT), NR-1, NR-7, NR-17, NR-32 e Resolução Cofen 736/2024 fundamentam a análise de temas, **não** certificam que os cursos das instituições incluíram cada microtópico. Para a LDRT, utilizar o anexo atualizado em 2024 em vez de se basear apenas na redação de 2023. A Portaria reconhece expressamente que a lista não substitui a avaliação científica de causalidade.

**Direitos:** distinguir o uso de metadados, títulos e referências do uso/republicação de textos originais protegidos. Lei 9.610/1998, arts. 8, 29 e 46–47; o material autoral pode ser preparado com referências, mas direitos de reprodução da fonte original continuam não liberados.

## Gates remanescentes

- Identidade e span curricular específico para cinco candidatos de disciplina;
- Revisão de relações alternativas (`ALIGNS_WITH`, `RELATED_TOPIC`) antes de qualquer promoção à ontologia;
- Suporte normativo frase a frase para átomos educacionais autorais e revisão clínica onde necessária;
- QA CI e aprovação editorial/humana para publicação.

Registro machine-readable: `audit/EVIDENCE_AND_TYPE_DISPOSITION_12_v0.3.6.json`. Todos os 985 itens, 42 títulos, 27 pares e a v0.3.4 mantidos. **Sem merge, deploy, escrita no Supabase ou criação de novas relações canônicas.**
