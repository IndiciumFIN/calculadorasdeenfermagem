# Setup: CLONE_PAT — GitHub Personal Access Token

## Por que é necessário

O `CLONE_PAT` é o secret que permite workflows do GitHub Actions fazerem `git clone` deste repositório.

Sem ele, nenhum workflow consegue:
1. Clonar o repo para rodar WOs
2. Executar `kernel canonical` com os 104.668 átomos
3. Rodar `kernel gate` automaticamente

## Passos

### 1. Criar o PAT

1. Vai em **GitHub.com → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **Generate new token**
3. Configurações:
   - **Name**: `ce-kernel-clone-pat`
   - **Expiration**: 90 dias (vai expirar — anota no calendário)
   - **Resource owner**: `IndiciumFIN`
   - **Repository access**: "Only select repositories" → `calculadorasdeenfermagem`
   - **Permissions**:
     - `contents`: Read and write
     - `workflows`: Read and write
4. Click **Generate token**
5. **Copia o token agora** — só mostra uma vez

### 2. Adicionar como secret

1. Vai em **GitHub.com → IndiciumFIN/calculadorasdeenfermagem → Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `CLONE_PAT`
4. Secret: cola o token que copiou
5. Click **Add secret**

### 3. Ativar branch protection na main

1. Vai em **Settings → Branches → Add branch protection rule**
2. Rule name: `main`
3. Marca:
   - ✅ "Require a pull request before merging" (pode desativar depois se quiser push direto)
   - ✅ "Require status checks to pass before merging" → adiciona: `gate-agregador`
   - ✅ "Require branches to be up to date before merging"
4. Click **Create**

### 4. Após criar o PAT — executar FASE A

```bash
# Depois de ter o CLONE_PAT registrado, me avisa.
# Vou criar a branch cursor/atomizacao-full e
# subir todo o código, depois fazer o PR → main.
```

## Renovação

Quando o PAT expirar (após 90 dias), você vai receber uma notificação do GitHub.
Regenera o PAT e atualiza o secret `CLONE_PAT`.
