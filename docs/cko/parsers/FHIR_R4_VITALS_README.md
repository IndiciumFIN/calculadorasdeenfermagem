# CKO — Parser FHIR R4 de Sinais Vitais (candidato técnico)

**Status:** `TECHNICAL_CANDIDATE / HOLD_HUMAN / NO_PUBLICATION`. WO #44. Dependente da PR estrutural #40.

## Referência primária
- [HL7 FHIR R4 v4.0.1 — Observation vital signs](https://hl7.org/fhir/R4/observation-vitalsigns.html)
- [HL7 FHIR R4 — VitalSigns StructureDefinition](https://hl7.org/fhir/R4/vitalsigns.html)
- Contrato `contracts/fontes/fhir_vitais.json` e política `KERNEL-POLICY-008` v1.1.0.

## Entrada aceita
- `Observation` JSON FHIR R4 ou `Bundle` (`collection`/`searchset`) com Observations.
- Identificadores de fonte/documento passados **externamente** pelo gerenciador de proveniência.
- Categoria vital-signs, status elegível, código LOINC, referência Patient relativa, effectiveDateTime com fuso, Quantity numérico finito + UCUM, ou motivo codificado de ausência.
- Subconjunto explícito: frequência cardíaca, respiratória, SpO2, temperatura, peso, altura, perímetro cefálico, IMC e pressão arterial (dois componentes). Outros perfis (p.ex. panel sem observações) recebem HOLD, não correção inventada.
- API pura: `parse(raw, source_id="...", document_id="...")`; sem acesso à rede ou a dados externos.

## Saída / segurança
- Resultado determinístico com hash SHA-256 do registro, código, unidade, medida e IDs da proveniência fornecida.
- Não copia `subject.reference`, `Observation.id`, notas livres nem outros identificadores. **O hash não é anonimização**. Uso com dados reais exige revisão de privacidade, base legal, controles de acesso e tratamento seguro.
- Cada registro recebe `HOLD_HUMAN`, `clinical_approved=false`, `publication_allowed=false`. Nenhuma entidade clínica é promovida.
- Uma entrada inválida de `Bundle` faz a operação falhar como um todo, sem retorno parcial.

## Lacunas documentadas / bloqueios
- Validação clínica e terminológica integral, licenças LOINC, políticas de privacidade, autenticação FHIR e teste com arquivos oficiais reais não homologados.
- Não suporta todos os perfis FHIR nem `effectivePeriod`/intervalos, referência Patient absoluta, painel `85353-1`, traduções de código ou extensões desconhecidas; lança `ParseHold`.
- Os validadores `schema_validator` e `loinc_validator` continuam sem self-tests aprovados. Por isso, o Kernel não admite a política #008, mesmo quando o parser extrai um recurso estruturalmente válido.
- CI de parser **não** substitui a verificação estrita de 20 contratos de fontes.

## Verificação
```bash
python -m unittest discover -s tests -p 'test_fhir*py' -v
python scripts/verify_repository_integrity.py --strict
```
O segundo comando continua esperado em FAIL até implementação de todas as demais dependências, sem mascarar suas exceções.
