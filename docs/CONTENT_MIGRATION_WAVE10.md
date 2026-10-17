# Mapeamento da migração de conteúdos — Wave 10 (somente evidência)

Esta onda amplia a aquisição para currículo, artigos/páginas, JS, identidade visual, i18n, cards, materiais clínicos, banco de urgência/emergência, políticas de publicação e Vila do Cuidado.

## Invariantes
- A autoridade da mutação é sempre uma WO qualificada executada pelo Kernel.
- Cada origem é identificada por file ID, título original, hash SHA-256 completo e tamanho.
- Conteúdo editorial não vira norma automaticamente. TOOL != CONTENT.
- Direitos/licença, revisão clínica, revisão editorial, acessibilidade e idiomas são gates independentes. Nunca inferir publicado por presença no Drive/Git.
- Raw fica em staging privado. O repositório público recebe apenas WOs e índices de evidência.
- ZIP deve ter manifesto de membros com hashes e verificações de segurança sem executar código nem extrair para disco.
- Deduplicar só por SHA-256 exato, preservando TODAS as relações de origem. Não escolher versão vencedora por nome.
- Excluir/mover origem somente por WO específica após segunda cópia independente durável, restauração testada, verificação de hash e confirmação humana de direitos/retention.
- Conteúdo do Drive além das normas faz parte do perímetro; inclui assets, traduções e scripts (.py, .js, .sh) inspecionados como dados, sem execução.

## Recorte
12 importações, 4 auditorias ZIP, 14.923.326 bytes originais, 485 membros auditados. Todas as importações e auditorias foram executadas no runtime privado do Kernel; nenhuma exclusão.
