# Pacote de revisão — tabelas transcritas manualmente (sepse e sinais vitais)

Gerado em 10/10/2026 (horário de Brasília, BRT) pelo Grok Bot. **Esta é só a 1ª passada automática. O veredito final é humano.** Use as colunas `veredito_humano`, `revisor` e `data_revisao` da planilha.

## O que tem aqui
- `REVISAO_TABELAS_TRANSCRITAS.xlsx`: uma aba de resumo + uma aba por tabela (SOFA, qSOFA, definicoes_sepsis3, NEWS2_pontos, NEWS2_risco, PA_DBHA2020).
- `revisao_<tabela>.csv`: cópias em CSV (UTF-8 com BOM) com as mesmas colunas.
- `revisar.py`: o script que gerou tudo, para dar para reproduzir.
- `fontes/`: os PDFs das fontes primárias usadas, com os cabeçalhos HTTP do download.
- `cofen736/`: a evidência da tarefa (1), a conferência da Res. Cofen 736/2024.

Colunas: `atom_id`, `campo`, `valor_transcrito`, `trecho_literal_fonte`, `pagina`, `arquivo_fonte`, `sha256_fonte`, `status_auto` (confere / diverge / nao_localizado), `observacao`.

## Resultado da 1ª passada
| tabela | confere | diverge | nao_localizado | total |
|---|---|---|---|---|
| SOFA | 32 | 0 | 2 | 34 |
| qSOFA | 5 | 0 | 1 | 6 |
| definicoes_sepsis3 | 7 | 1 | 0 | 8 |
| NEWS2_pontos | 36 | 0 | 0 | 36 |
| NEWS2_risco | 4 | 0 | 0 | 4 |
| PA_DBHA2020 | 25 | 1 | 0 | 26 |

### Pontos de atenção (divergências e não localizados)
1. **definicoes_sepsis3, choque séptico (DIVERGE, omissão):** a fonte (Box 3) diz *"persisting hypotension requiring vasopressors to maintain MAP ≥65 mm Hg"*. A transcrição diz só "necessidade de vasopressor para manter PAM >= 65 mmHg" e não fala em "hipotensão persistente". Os números conferem.
2. **PA_DBHA2020, nota de rodapé (DIVERGE, omissão):** a nota * do Quadro 3.4 (*"A classificação é definida de acordo com a PA no consultório e pelo nível mais elevado de PA, sistólica ou diastólica."*) e as notas ** e *** (HA sistólica e diastólica isoladas) não foram transcritas. Isso importa na hora de classificar.
3. **SOFA, "total 0-24" (NAO_LOCALIZADO):** esse total é uma conta (6 sistemas × 4 pontos). Não existe trecho literal na fonte.
4. **SOFA, Vincent 1996 (NAO_LOCALIZADO):** o artigo original (Intensive Care Med 1996;22:707-710, doi 10.1007/BF01709751) é fechado. O OpenAlex marca como "closed" e a Springer devolveu uma página de desafio em HTML, não o PDF. **Por isso o SOFA foi conferido contra a Table 1 do Sepsis-3**, que traz a nota *"Adapted from Vincent et al."*. O original de 1996 não foi conferido.
5. **qSOFA, "1 ponto por item" (NAO_LOCALIZADO):** a fonte fala em *"at least 2 of the following clinical criteria"*. "1 ponto por item" é uma interpretação, sem trecho literal.
6. Observações que não viraram divergência:
   - O SOFA respiratório na fonte traz também os valores em kPa, que não foram transcritos.
   - A fonte do Quadro DBHA tem o erro tipográfico "PAS (mHg)".
   - A transcrição cita "Tabela", mas na fonte é o "Quadro 3.4".
   - O NEWS2 risco não transcreveu a coluna "Response".
   - "baixo-médio" corresponde ao "Red score" da fonte.
   - A transcrição de NEWS2 "Confusão nova, V, P ou U" foi casada com "CVPU" do Chart 1.

## Como foi feita a comparação automática
- Os trechos literais foram **extraídos pelo `pdftotext` (poppler 25.03)** das páginas indicadas. As células das tabelas foram recortadas por coordenadas de palavra (`-bbox`) e os textos corridos por região da página. Nenhum trecho foi digitado à mão. Quando o script não achou o trecho, a linha ficou `nao_localizado`.
- Regra:
  - Os números e operadores da transcrição e da fonte são normalizados (vírgula→ponto, ≥/ⱖ→>=, ≤/ⱕ→<=, travessão→hífen) e comparados em sequência.
  - Os números entre colchetes ou parênteses (unidade alternativa) são comparados à parte.
  - Termos-chave em pt-BR precisam ter o equivalente em inglês no trecho (ex.: "suporte ventilatório"→"respiratory support", "com O2"→"on oxygen").
  - No NEWS2, a pontuação vem da coluna da célula no Chart 1.
- Também é feita uma checagem reversa: uma célula da fonte sem átomo correspondente vira `diverge`. Nenhuma apareceu.
- **Teste de sensibilidade:** em uma cópia temporária dos átomos (os originais não foram alterados), mudei a temperatura ≥39,1 de 2 para 3 pontos e o conector da "PA ótima" de "e" para "e/ou". O script marcou as duas como `diverge`. Testes unitários com limiares errados (ex.: "<30" contra "<300", "epinefrina <=0,2" contra "≤0.1") também deram `diverge`.
- As definições são traduções. `confere` ali quer dizer que os elementos e números batem; a equivalência de sentido precisa ser confirmada por você.

## Fontes usadas (downloads em 10/10/2026, 16:41–16:43 BRT)
| arquivo | origem | bytes | sha256 |
|---|---|---|---|
| Sepsis3_Singer2016_JAMA_VoR_via_AmsterdamUMC.pdf | https://pure.amsterdamumc.nl/ws/files/186772133/The-third-international-consensus-definitions-for-sepsis-and-septic-shock-sepsis-3.pdf | 509717 | 597217c81b2e30e520ab1d209f183630ac4c6d939336e6119a33b29a38bdd833 |
| NEWS2_RCP2017_Chart1_scoring_system.pdf | https://www.rcp.ac.uk/media/alxev00t/news2-chart-1_the-news-scoring-system_0_0.pdf | 176840 | 62425a54bd29d5c64c175991fb532b776afb0f8fba4445328c94e9af67ddc53d |
| NEWS2_RCP2017_Chart2_thresholds_triggers.pdf | https://www.rcp.ac.uk/media/2acdezkd/news2-chart-2_news-thresholds-and-triggers_0.pdf | 100309 | 069ab296933c5e8e3b65731df1f92bb11bc0482f8ed58ec0ddce06651922c523 |
| NEWS2_RCP2017_Final_report.pdf (referência; não usado na comparação) | https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf | 2588875 | c5dad854ccf0d210142d71434317b3407b8601416c9613b9c528f7cbec24de18 |
| DBHA2020_ArqBrasCardiol_116-3_516-658.pdf | https://abccardiol.org/wp-content/uploads/articles_xml/0066-782X-abc-116-03-0516/0066-782X-abc-116-03-0516.x98474.pdf (doi 10.36660/abc.20201238) | 3972880 | b62921e259f1c41e384fff56f3bcb0b8ed4686fad670607a2e2f09ead153ee0d |

Notas sobre as fontes:
- **Sepsis-3:** o PDF da JAMA (jamanetwork.com) e o do PMC/Europe PMC estavam bloqueados para download automático (403 ou desafio em JavaScript). O arquivo usado veio do repositório institucional da Amsterdam UMC, indicado pelo OpenAlex/Unpaywall. A capa do repositório diz *"Document Version: Publisher's PDF, also known as Version of record"* (licença Taverne). A página 1 do PDF é essa capa. As páginas 2–11 do PDF são as páginas 801–810 da JAMA 315(8). A coluna `pagina` mostra as duas numerações.
- **NEWS2:** a comparação usou os Charts 1 e 2 oficiais da RCP, 1 página cada. O relatório completo vai junto só como referência.
- **DBHA 2020:** a página 30 do PDF é a página 545 da revista (Quadro 3.4).
- O corpus Calculadoras-de-Enfermagem não tinha PDFs de Sepsis-3 nem de NEWS2, só páginas HTML do site. Por isso foram usados os downloads oficiais e públicos.

## Tarefa (1): Res. Cofen 736/2024
Os detalhes estão em `cofen736/EVIDENCIA_COFEN_736_2024.md` e `.json`.
- A cópia local (sha256 3fb4e597…7a49, 718.575 bytes) é **IDÊNTICA** byte a byte ao PDF baixado agora de cofen.gov.br.
- Em relação à página 74 da Seção 1 do DOU de 23/01/2024, é **mesmo conteúdo com bytes diferentes**: o texto extraído é idêntico.

Aviso: o material de apoio não substitui a avaliação clínica nem os protocolos institucionais.
