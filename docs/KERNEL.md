# Kernel (CLI) — Ponto Único de Entrada

O Kernel é a CLI em `packages/cli/`. Ele é o único caminho autorizado para que qualquer conteúdo (normativo, escala, conteúdo, conversa exportada) chegue ao Registry e, depois, ao Supabase.

## Responsabilidades

1. Receber fonte (URL ou arquivo).
2. Aplicar máscara/template de extração.
3. Chamar o parser adequado (HTML, texto, futuro OCR/PDF).
4. Gerar átomos com auditoria.
5. Validar contra invariantes.
6. Exigir registro no Registry antes de qualquer persistência.

## O que o Kernel não faz

- Não publica diretamente.
- Não decide status semântico final (Vigente/Revogado) sem evidência.
- Não ignora falha de validação.

## Extensão futura

Novos adapters (OCR, PDF layout, APIs oficiais) devem ser chamados **por dentro** do Kernel, nunca como scripts soltos que escrevem direto no Supabase.
