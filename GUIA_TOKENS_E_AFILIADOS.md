# Guia Passo a Passo: Como Pegar as Tags de Afiliado e os Tokens de API

Este guia mostra exatamente **onde clicar** em cada site para pegar a parte do link que contabiliza a sua comissão e os Tokens para o robô postar sozinho.

---

## PARTE 1: Como Pegar a Parte do Link que Conta Comissão (Afiliados)

### 1. Amazon Associados (`AMAZON_ASSOCIATE_TAG`) — *O Mais Fácil e Rápido*
1. Acesse **[associados.amazon.com.br](https://associados.amazon.com.br/)** e entre com sua conta da Amazon.
2. Quando pedir **URL do seu site/rede social**, cole o link da sua Página do Facebook, Pinterest ou Canal do WhatsApp.
3. Assim que entrar no painel da Amazon Associados, olhe no **canto superior direito da tela** (bem ao lado do seu endereço de e-mail).
4. Estará escrito: **`ID de associado: seunome-20`** (sempre termina com `-20` no Brasil).
5. **O que conta no link:** Qualquer link da Amazon que tenha `?tag=seunome-20` no final já dá comissão para você!
   * Basta colocar esse `seunome-20` na variável `AMAZON_ASSOCIATE_TAG=` dentro do arquivo `.env`.

---

### 2. Mercado Livre Afiliados (`MERCADOLIVRE_AFFILIATE_ID`)
1. Cadastre-se em **[mercadolivre.com.br/afiliados](https://www.mercadolivre.com.br/afiliados)**.
2. Depois de aprovado, quando você abrir qualquer produto no site do Mercado Livre, aparecerá uma barra cinza no topo da tela (**Barra de Afiliado**).
3. Clique em **"Gerar Link"** e copie o **Link Completo** (ou abra o link curto no navegador para ele expandir).
4. Olhe no final do endereço do link: você verá algo como:
   `...&matt_word=SEUNOME&matt_tool=84729104`
5. **O que conta no link:** Esse código depois de `matt_tool=` (e `matt_word=`) é a assinatura da sua conta! Basta colar na variável `MERCADOLIVRE_AFFILIATE_ID=` no arquivo `.env`.

---

### 3. Kabum, Magalu, AliExpress e +100 Lojas (Via Lomadee)
1. Crie sua conta gratuita em **[lomadee.com](https://www.lomadee.com/)**.
2. No menu lateral, vá em **Meus Canais / Espaços**.
3. Lá você verá um número chamado **`sourceId`** (ex: `37482910`).
4. **O que conta no link:** Na Lomadee, qualquer link que contenha o seu `sourceId` registra a comissão na sua conta.

---

## PARTE 2: Como Pegar os Tokens de API (Para Postar Sozinho)

### 1. Facebook (`FACEBOOK_PAGE_ID` e `FACEBOOK_PAGE_ACCESS_TOKEN`)

#### Passo A — Pegar o `FACEBOOK_PAGE_ID` (Leva 30 segundos):
1. Abra a sua Página no Facebook.
2. Clique na aba **Sobre** $\rightarrow$ **Transparência da Página**.
3. Copie o número que aparece em **ID da Página** (ex: `123456789012345`) e cole em `FACEBOOK_PAGE_ID=` no `.env`.

#### Passo B — Pegar o `FACEBOOK_PAGE_ACCESS_TOKEN`:
1. Acesse **[developers.facebook.com](https://developers.facebook.com/)** $\rightarrow$ clique em **Meus Aplicativos** $\rightarrow$ **Criar Aplicativo**.
2. Selecione **"Outro"** $\rightarrow$ **"Empresa (Business)"** $\rightarrow$ dê o nome de `Robo Ofertas` e crie.
3. Agora acesse direto o **[Graph API Explorer](https://developers.facebook.com/tools/explorer/)**.
4. Na coluna da direita:
   * Em **Aplicativo da Meta**, selecione o `Robo Ofertas`.
   * Em **Usuário ou Página**, clique e mude para **"Obter Token de Acesso da Página"** (autorize a sua Página de Ofertas).
   * Em **Permissões (Permissions)**, adicione:
     * `pages_manage_posts`
     * `pages_read_engagement`
   * Clique no botão azul **"Generate Access Token"** e selecione o nome da sua Página no menu **Usuário ou Página**.
5. Copie o código grande que apareceu na barra superior (**Token de Acesso**) e cole em `FACEBOOK_PAGE_ACCESS_TOKEN=` no `.env` (e mude `FACEBOOK_ATIVO=true`).

---

### 2. Pinterest (`PINTEREST_ACCESS_TOKEN` e `PINTEREST_BOARD_ID`)

1. Com sua conta do Pinterest Business logada, acesse **[developers.pinterest.com/apps/](https://developers.pinterest.com/apps/)**.
2. Clique em **Connect app (Criar aplicativo)** e preencha o formulário rápido dizendo que o app é para publicar seus próprios Pins de produtos.
3. Assim que abrir a página do seu App no Pinterest Developers, role até a parte **Generate Access Token**.
4. Marque as caixinhas: `boards:read`, `boards:write`, `pins:read`, `pins:write` e clique em **Generate Token**.
5. Copie o código que começa com `pina_...` e cole em `PINTEREST_ACCESS_TOKEN=` no `.env`.
6. Para o `PINTEREST_BOARD_ID`, crie uma pasta no seu Pinterest (ex: *"Ofertas e Promoções"*). Assim que você colar o Token acima, eu rodo 1 comando aqui para descobrir o número do ID dessa pasta automaticamente para você!
