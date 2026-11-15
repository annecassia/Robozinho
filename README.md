# 🤖 Robô Autônomo de Ofertas e Cupons de Afiliados (Anne Wealth)

Robô inteligente para garimpo automatizado de promoções com altos descontos (>25%) e cupons verificados nas maiores lojas do Brasil, formatando links de comissão e publicando nos canais oficiais sem intervenção humana.

---

## 🚀 Plataformas de Publicação Integradas
* 🟢 **WhatsApp Channels:** Publicação de imagens e legendas formatadas via Baileys no canal oficial.
* 🔵 **Facebook Pages:** Publicação automática de posts com imagens via Meta Graph API.
* 📸 **Instagram Feed:** Publicação automática de ofertas e cupons no feed comercial/criador (`@loja.annes`).
* 📌 **Pinterest:** Publicação automática de Pins na pasta de achados e catálogo (API v5).

---

## 🛒 Redes e Lojas Integradas
* **Rede Lomadee (API v3/2026):** Extração de campanhas, cupons reais e links curtos oficiais para dezenas de marcas (Drogasmil, PCYES, Moto BR, Sawary, SpeedMax, PneuStore, etc.).
* **Amazon Brasil:** Rastreamento com tag oficial de associado.
* **Mercado Livre:** Rastreamento de ofertas com Envio Full e central de cupons.
* **Shopee:** Cupons diários oficiais e descontos em lojas oficiais.

---

## 🧠 Recursos Inteligentes
1. **Controle Anti-Repetição (Janela de 1 Hora):** Impede o reenvio do mesmo link, produto ou cupom na janela de 60 minutos, com auto-limpeza automática.
2. **Rotação de Lojas:** Alternância dinâmica de marcas (nunca envia a mesma loja duas vezes seguidas).
3. **Intervalo Humanizado:** Delay inteligente de 90 segundos entre produtos e cupons para evitar flood e parecer 100% orgânico.
4. **Download da 1ª Foto Original:** Garimpa e baixa a primeira foto oficial de alta definição do anúncio.
5. **Gerador de Badges de Cupons:** Cria molduras em alta definição (800x800) personalizadas com a logo de cada loja.

---

## 🛠️ Instalação e Execução

### Pré-requisitos
* Python 3.10+
* Node.js 18+

### 1. Clonar e Instalar Dependências
```bash
git clone <URL_DO_REPOSITORIO>
cd revisao

# Instalar dependências Python
pip install -r requirements.txt

# Instalar dependências Node (Baileys)
npm install
```

### 2. Configurar Variáveis de Ambiente
Copie o arquivo de exemplo e preencha com suas credenciais:
```bash
cp .env.example .env
```

### 3. Conectar o WhatsApp (Apenas na 1ª vez)
```bash
node whatsapp_sender.js --conectar
```
Escaneie o QR Code no seu WhatsApp (Aparelhos Conectados). A sessão ficará salva localmente.

### 4. Executar

* **Executar 1 ciclo avulso de teste:**
  ```bash
  python main.py
  ```

* **Executar em modo contínuo (Loop 24/7):**
  ```bash
  python main.py --loop
  ```

---

## 📄 Licença
Uso próprio da marca **Anne Wealth**. Todos os direitos reservados.
