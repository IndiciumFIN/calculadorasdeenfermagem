# Fonte primária W5/W6 — revisão v0.2.3
**Uso: auditoria e recuperação documental. Não utilizar como aprovação clínica/normativa.**

## Limites do exame
- Os oito NormAtoms W5 foram relidos diretamente da branch W5 no GitHub (blob `95f9d314e1c967be7c52c4519d4875336461dfcc`). Sete remetem aos dispositivos da RDC 15/2012 identificados na cópia PDF oficial hospedada no repositório de legislação do Ministério da Saúde: https://bvsms.saude.gov.br/bvs/saudelegis/anvisa/2012/rdc0015_15_03_2012.pdf. O documento exibe expressamente a ressalva de que a cópia não substitui a publicação no DOU.
- Os artigos/localizadores do PDF foram conferidos na camada textual e a capa foi inspecionada visualmente. Isso atesta **localizador encontrado**, não equivalência jurídica, cadeia de custódia, interpretação clínica nem vigência consolidada. Nenhum hash de fonte/fragmento foi criado sem bytes primários adquiridos.
- O átomo W5-08 aponta para a notícia da Anvisa: https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2016/reprocessamento-de-produto-para-saude-deve-seguir-regra . No portal visualizado, a data exibida de publicação é 04/07/2022, embora a rota contenha 2016; a página consultada é resumo informativo, insuficiente como fonte jurídica de todas as regras de reprocessamento. Verificar RDC 156/2006, RE 2605/2006 e RE 2606/2006 e seu estado atual.
- As seis fontes W6 foram relidas diretamente da branch W6 no GitHub (blob `021f6a4ffef7d225a0a02ea99622f0538cb79b35`). Três IDs coincidem exatamente com `cko_evidence.sources` no Supabase: `SRC-COFEN-RES-736-2024`, `SRC-COFEN-RES-754-2024`, `SRC-ANVISA-RDC-36-2013`; nos três registros o status de acreditação é `PENDING_BOARD_REVIEW`. Os outros três IDs não foram encontrados na consulta filtrada por ID. Isso não é prova de ausência fora do catálogo.
- O COFEN 581/2018 tem alterações listadas na própria página, e seu Anexo aponta especialidades 8 (CME), 9 (Centro Cirúrgico) e recuperação pós-anestésica como subitem. A lista deve ser tratada como panorama profissional com histórico normativo: https://www.cofen.gov.br/resolucao-cofen-no-581-2018/
- O protocolo de cirurgia segura do MS está referenciado na biblioteca digital da Anvisa como publicação de **2013**, e a página do Ministério mostra metadado de atualização 23/03/2026; esse metadado **não prova atualização do conteúdo**. https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/1771
- A OMS disponibiliza o manual de implantação de 2009 como orientação internacional, não lei brasileira: https://www.who.int/publications/i/item/9789241598590

## Estado
Todos os 8 NormAtoms e 6 sources W6 mantêm **hash de fragmento não verificado**, direitos e homologação clínica pendentes. Este pacote só contém IDs, URLs, escopos resumidos e estados; **não** inclui PDF, HTML original, trechos longos de normas, credenciais ou dados de pacientes.

## Próxima microtarefa
Adquirir as versões oficiais íntegras em local autorizado; registrar SHA-256 de bytes brutos, URL/cabeçalho/data, licença, versão/alterações, localizador preciso e SHA-256 de fragmento de texto segundo método reproduzível; revisão humana separada para direitos, normativo e conteúdo.
