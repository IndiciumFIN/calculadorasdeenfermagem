# Anvisa dispositivos médicos — parser de metadados candidatos

**Fonte oficial:** https://dados.anvisa.gov.br/dados/TA_PRODUTO_SAUDE_SITE.csv  
**Dicionário:** https://dados.anvisa.gov.br/dados/Documenta%C3%A7%C3%A3o_e_Dicion%C3%A1rio_de_Dados_Produto_para_Sa%C3%BAde_V1.0.pdf  
**Explicação oficial de duplicações:** https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2020/banco-de-dados-traz-informacoes-de-produtos-para-saude

Contrato `contracts/fontes/anvisa_dev.json`; parser `packages/cli/parsers/anvisa_dev.py`; política `KERNEL-POLICY-009@1.1.0`.

## Subconjunto técnico

Entrada: captura local imutável do CSV de dispositivos médicos. Parâmetros: `source_id`, `document_id`, `captured_at` com fuso horário, `expected_sha256` do arquivo, `encoding` explicitamente em `cp1252` ou `utf-8-sig`. O módulo não faz download e não autentica a origem do documento. O SHA confere somente os bytes fornecidos.

O cabeçalho deve incluir exatamente os campos de identificação/regulamentação descritos no dicionário Anvisa, mais opcionalmente `DT_ATUALIZACAO_DADO`. Este conjunto é conservador; novas versões devem ser objeto de reconciliação de schema antes do uso.

Os identificadores registro/cadastro, processo e CNPJ são tratados como strings (com zeros à esquerda). `CLASSE_RISCO` recebe I, II, III ou IV sem interpretação clínica. Nomes técnico/comercial e de fabricantes, CNPJ, validade e datas são validados quanto à presença/formato básico quando necessário, mas **não são exportados**. Um registro pode ter várias linhas de fabricantes diferentes; o parser preserva a multiplicidade e gera `source_occurrence_index` e hash de identidade do fabricante, evitando apagar evidência. Nenhuma deduplicação automática no material-fonte é permitida.

## HOLD obrigatório

- A Anvisa publica a base D-1, sujeita a mudanças. O snapshot precisa ser identificado e seu hash reconciliado.
- Código/risco no CSV não representa autorização de uso clínico, adequação a paciente, disponibilidade, validade atual ou ausência de recall.
- `source_origin_verified=false`, `registry_current_verified=false`, `rights_verified=false`, `clinical_approved=false`, `publication_allowed=false`, `release_allowed=false` e `status=HOLD_HUMAN` sempre.
- `schema_validator` ainda não está admitido pelo Kernel; direitos de operação, WO e revisão profissional são exigidos antes de qualquer promoção.
- A implementação foi testada com fixtures sintéticas. Para aceitar dados reais, é indispensável confrontar versão, encoding e cabeçalhos com o arquivo Anvisa oficialmente capturado, sem presumir equivalência apenas por nomes de colunas.

Testes `test_anvisa_dev_parser.py`, `test_anvisa_dev_policy_failclosed.py`. Não há processamento de informações de pacientes nem publicação de texto clínico.
