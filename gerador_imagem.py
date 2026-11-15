from io import BytesIO
from pathlib import Path
import re
import requests
from PIL import Image, ImageDraw, ImageFont
from config import CARDS_DIR, OUTPUT_DIR

LOGOS_DIR = OUTPUT_DIR / "logos"
LOGOS_DIR.mkdir(parents=True, exist_ok=True)

# Identidade visual oficial de cada loja
ESTILOS_LOJAS = {
    "shopee": {
        "bg": (238, 77, 45),       # Laranja oficial Shopee (#EE4D2D)
        "fg": (255, 255, 255),
        "accent": (255, 235, 59),
        "nome": "Shopee",
        "sub": "CUPOM DE DESCONTO OFICIAL",
    },
    "mercadolivre": {
        "bg": (255, 230, 0),       # Amarelo oficial Mercado Livre (#FFE600)
        "fg": (45, 50, 119),       # Azul oficial Mercado Livre (#2D3277)
        "accent": (45, 50, 119),
        "nome": "Mercado Livre",
        "sub": "CUPOM DE DESCONTO OFICIAL",
    },
    "amazon": {
        "bg": (19, 25, 33),        # Azul escuro oficial Amazon (#131921)
        "fg": (255, 255, 255),
        "accent": (255, 153, 0),   # Laranja sorriso Amazon (#FF9900)
        "nome": "amazon.com.br",
        "sub": "CUPOM DE DESCONTO OFICIAL",
    },
    "kabum": {
        "bg": (0, 96, 177),        # Azul oficial KaBuM!
        "fg": (255, 255, 255),
        "accent": (255, 101, 0),   # Laranja oficial KaBuM!
        "nome": "KaBuM!",
        "sub": "CUPOM DE DESCONTO OFICIAL",
    },
    "magalu": {
        "bg": (0, 134, 255),       # Azul oficial Magalu
        "fg": (255, 255, 255),
        "accent": (255, 230, 0),
        "nome": "Magalu",
        "sub": "CUPOM DE DESCONTO OFICIAL",
    },
    "aliexpress": {
        "bg": (230, 46, 4),        # Vermelho oficial AliExpress
        "fg": (255, 255, 255),
        "accent": (255, 215, 0),
        "nome": "AliExpress",
        "sub": "CUPOM DE DESCONTO OFICIAL",
    },
    "drogasmil": {
        "bg": (0, 122, 135),
        "fg": (255, 255, 255),
        "accent": (255, 215, 0),
        "nome": "Drogasmil",
        "sub": "CUPOM DE FARMÁCIA & BELEZA",
    },
    "pcyes": {
        "bg": (18, 18, 18),
        "fg": (255, 255, 255),
        "accent": (225, 29, 72),
        "nome": "PCYES Gamer",
        "sub": "CUPOM OFICIAL HARDWARE",
    },
    "sawary": {
        "bg": (26, 32, 44),
        "fg": (255, 255, 255),
        "accent": (236, 72, 153),
        "nome": "Sawary Jeans",
        "sub": "OFERTA & CUPOM EXCLUSIVO",
    },
    "pneustore": {
        "bg": (20, 20, 20),
        "fg": (255, 255, 255),
        "accent": (250, 204, 21),
        "nome": "PneuStore",
        "sub": "CUPOM AUTOMOTIVO OFICIAL",
    },
}


def carregar_fonte(tamanho: int, negrito: bool = True):
    candidatas = (
        ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
        if negrito
        else ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
    )
    for nome in candidatas:
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def baixar_primeira_foto_anuncio(oferta: dict) -> Path:
    """
    Baixa diretamente a PRIMEIRA FOTO ORIGINAL do produto.
    Não altera, não corta e não aplica filtros.
    """
    url_foto = oferta.get("imagem_url")
    caminho_final = CARDS_DIR / f"{oferta['id']}_foto_original.jpg"

    if caminho_final.exists() and caminho_final.stat().st_size > 5000:
        return caminho_final

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url_foto, headers=headers, timeout=15)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img.save(caminho_final, format="JPEG", quality=95)
            return caminho_final
    except Exception as e:
        print(f"Aviso ao baixar foto ({url_foto}): {e}")

    # Fallback caso a foto não carregue
    img_fallback = Image.new("RGB", (800, 800), (245, 247, 250))
    img_fallback.save(caminho_final, format="JPEG", quality=90)
    return caminho_final


def detectar_slug_loja(texto: str) -> str:
    """Identifica a loja a partir de palavras-chave no texto ou URL."""
    t = texto.lower()
    if any(k in t for k in ["shopee", "shope"]):
        return "shopee"
    if any(k in t for k in ["mercado livre", "mercadolivre", "meli", "full", "meli+"]):
        return "mercadolivre"
    if any(k in t for k in ["kabum", "tonokabum", "ninja"]):
        return "kabum"
    if any(k in t for k in ["amazon", "prime", "alexa", "kindle"]):
        return "amazon"
    if any(k in t for k in ["drogasmil", "farmacia"]):
        return "drogasmil"
    if any(k in t for k in ["pcyes", "gamer"]):
        return "pcyes"
    if any(k in t for k in ["sawary", "jeans"]):
        return "sawary"
    if any(k in t for k in ["pneustore", "speedmax", "motobr", "pneu"]):
        return "pneustore"
    if any(k in t for k in ["magalu", "magazine luiza", "magazine"]):
        return "magalu"
    if any(k in t for k in ["aliexpress", "ali express"]):
        return "aliexpress"

    slug_limpo = re.sub(r"[^a-z0-9]", "", t.split()[0] if t.split() else "loja")
    return slug_limpo or "loja"


def obter_logo_loja_cupom(cupom: dict) -> Path:
    """
    Identifica a loja pelas palavras-chave do cupom e retorna a imagem da Logo Oficial da loja
    pronta para enviar junto com o cupom.
    """
    texto_analise = f"{cupom.get('loja', '')} {cupom.get('codigo', '')} {cupom.get('beneficio', '')}"
    slug = detectar_slug_loja(texto_analise)
    nome_loja = cupom.get("loja", "Loja Parceira")

    estilo = ESTILOS_LOJAS.get(slug, {
        "bg": (15, 23, 42),       # Slate moderno
        "fg": (255, 255, 255),
        "accent": (225, 29, 72),  # Tom rubi Anne Wealth
        "nome": nome_loja,
        "sub": "CUPOM DE DESCONTO OFICIAL",
    })

    caminho_logo = LOGOS_DIR / f"logo_{slug}.jpg"
    if caminho_logo.exists():
        return caminho_logo

    largura, altura = 800, 800
    img = Image.new("RGB", (largura, altura), estilo["bg"])
    draw = ImageDraw.Draw(img)

    fonte_marca = carregar_fonte(90, negrito=True)
    fonte_sub = carregar_fonte(32, negrito=True)
    fonte_icone = carregar_fonte(85, negrito=True)

    # Moldura destacada
    draw.rounded_rectangle(
        [(60, 60), (740, 740)],
        radius=50,
        outline=estilo["accent"],
        width=8,
    )

    if slug == "shopee":
        draw.rounded_rectangle([(310, 195), (490, 395)], radius=26, fill=(255, 255, 255))
        draw.arc([(345, 135), (455, 245)], start=180, end=0, fill=(255, 255, 255), width=14)
        bbox_s = draw.textbbox((0, 0), "S", font=fonte_icone)
        ws = bbox_s[2] - bbox_s[0]
        draw.text(((largura - ws) / 2, 238), "S", fill=estilo["bg"], font=fonte_icone)

    nome_txt = estilo["nome"]
    bbox_n = draw.textbbox((0, 0), nome_txt, font=fonte_marca)
    wn = bbox_n[2] - bbox_n[0]
    y_nome = 435 if slug == "shopee" else 310
    draw.text(((largura - wn) / 2, y_nome), nome_txt, fill=estilo["fg"], font=fonte_marca)

    y_faixa = 585 if slug == "shopee" else 480
    draw.rounded_rectangle([(120, y_faixa), (680, y_faixa + 75)], radius=20, fill=estilo["accent"])
    cor_txt_faixa = (19, 25, 33) if slug in ("shopee", "amazon", "magalu") else (255, 255, 255)
    sub_txt = estilo["sub"]
    bbox_sub = draw.textbbox((0, 0), sub_txt, font=fonte_sub)
    wsub = bbox_sub[2] - bbox_sub[0]
    draw.text(((largura - wsub) / 2, y_faixa + 18), sub_txt, fill=cor_txt_faixa, font=fonte_sub)

    img.save(caminho_logo, format="JPEG", quality=95)
    return caminho_logo
