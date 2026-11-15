import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Diretórios de saída e histórico
OUTPUT_DIR = BASE_DIR / "output"
CARDS_DIR = OUTPUT_DIR / "cards"
DADOS_DIR = BASE_DIR / "dados"
HISTORICO_PATH = DADOS_DIR / "historico_postados.json"

for pasta in (OUTPUT_DIR, CARDS_DIR, DADOS_DIR):
    pasta.mkdir(parents=True, exist_ok=True)

# Configurações de Afiliado
AMAZON_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "seu-id-20").strip()
ML_AFFILIATE_ID = os.getenv("MERCADOLIVRE_AFFILIATE_ID", "").strip()
SHOPEE_AFFILIATE_PARAMS = os.getenv("SHOPEE_AFFILIATE_PARAMS", "").strip()
LOMADEE_SOURCE_ID = os.getenv("LOMADEE_SOURCE_ID", "").strip()
LOMADEE_APP_TOKEN = os.getenv("LOMADEE_APP_TOKEN", "").strip()
LINK_GRUPO_WHATSAPP = os.getenv("LINK_GRUPO_WHATSAPP", "https://chat.whatsapp.com/SEU_LINK_AQUI").strip()

# Filtro de Qualidade das Ofertas
DESCONTO_MINIMO = int(os.getenv("DESCONTO_MINIMO_PERCENTUAL", "25"))

# Termos de alto apelo de venda (Tech, Gamer, Casa, Eletrônicos)
TERMOS_BUSCA = [
    "mouse gamer logitech",
    "headset gamer hyperx",
    "teclado mecanico gamer",
    "fone bluetooth jbl",
    "monitor gamer 144hz",
    "ssd nvme 1tb",
    "cadeira gamer",
    "echo dot alexa",
    "air fryer fritadeira",
    "controle sem fio ps5 xbox",
]

# Credenciais WhatsApp (Green-API)
WHATSAPP_ATIVO = os.getenv("WHATSAPP_ATIVO", "false").lower() == "true"
GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID", "").strip()
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN", "").strip()
WHATSAPP_GROUP_ID = os.getenv("WHATSAPP_GROUP_ID", "").strip()

# Credenciais Facebook (Graph API)
FACEBOOK_ATIVO = os.getenv("FACEBOOK_ATIVO", "false").lower() == "true"
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "").strip()
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()

# Credenciais Instagram (@annecassialmeida)
INSTAGRAM_ATIVO = os.getenv("INSTAGRAM_ATIVO", "false").lower() == "true"
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()

# Credenciais Pinterest (API v5)
PINTEREST_ATIVO = os.getenv("PINTEREST_ATIVO", "false").lower() == "true"
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "").strip()
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID", "").strip()
