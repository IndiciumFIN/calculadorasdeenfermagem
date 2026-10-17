# Instrução para levantamento de localStorage e bibliotecas

## Objetivo

Inventariar o que já existe no site homologado (localStorage) e nas bibliotecas do ChatGPT para documentar templates com contratos.

## Como executar (usuário ou bot com acesso ao computador)

### 1. localStorage do site homologado

1. Abrir https://www.calculadorasdeenfermagem.com.br/ no navegador.
2. Abrir DevTools → Application → Local Storage.
3. Exportar as chaves e valores relevantes (ou screenshot + cópia).
4. Salvar em `inventory/localstorage_site.json` no repositório.

### 2. Bibliotecas do ChatGPT

Existem duas contas/bibliotecas mencionadas.

1. Em cada conta ChatGPT, exportar conversas ou projetos relevantes (se a opção estiver disponível).
2. Listar templates, prompts e materiais de design system já usados.
3. Salvar em `inventory/chatgpt_lib_1.md` e `inventory/chatgpt_lib_2.md`.

### 3. O que documentar de cada template encontrado

Para cada template:
- ID canônico proposto
- Dimensões
- Camadas principais
- Fonte de conteúdo (norma, escala, institucional)
- Status (homologado / rascunho / divergente do design system)

## O que não fazer

- Não publicar nada a partir desses inventários sem contrato e validação.
- Não tratar material do ChatGPT como canônico até passar pelo design system e Registry.
