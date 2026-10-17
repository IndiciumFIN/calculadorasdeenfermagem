# Ecossistema Canônico Governado por Normas

## Princípio central

Todo conteúdo (calculadora, escala, texto, imagem) deve poder ser rastreado até um átomo normativo ou uma fonte oficial validada.

## Camadas

1. **Fontes oficiais** (COFEN, DOU, Anvisa, etc.)
2. **Ingestão CLI** → texto limpo + hash
3. **Atomização** → JSON validado
4. **Master Data** (Supabase)
5. **Parâmetros de aplicação** (JSON oculto que alimenta calculadoras)
6. **Front** (Next.js) consome apenas dados validados
7. **Builder** produz peças visuais a partir de tokens + conteúdo aprovado

## Escalabilidade

- Novas fontes entram como novos comandos ou adapters na CLI.
- Novos tipos de conteúdo (escalas, quizzes) ganham schema próprio.
- Conversas antigas podem ser ingeridas e promovidas a átomos ou conteúdos depois de revisão.

## Recuperação de conversas

1. Exporte do ChatGPT (Settings → Data controls → Export).
2. Extraia os arquivos de interesse.
3. Rode `ingest` neles.
4. Classifique o que vira normativo, o que vira conteúdo editorial e o que é descartado.
5. Valide e publique.

Isso transforma histórico disperso em ativo governado.
