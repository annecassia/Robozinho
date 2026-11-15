import html
from config import LINK_GRUPO_WHATSAPP


def formatar_moeda(valor: float) -> str:
    """Formata float para padrão brasileiro R$ 1.234,56."""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def gerar_texto_whatsapp(oferta: dict) -> str:
    """
    Gera a mensagem limpa com o link direto para o produto.
    """
    preco_antigo_str = formatar_moeda(oferta["preco_original"])
    preco_atual_str = formatar_moeda(oferta["preco_atual"])
    desconto = oferta.get("desconto_pct", 0)

    linha_cupom = ""
    if oferta.get("cupom"):
        linha_cupom = f"\n🎟️ Cupom: *{oferta['cupom']}*"

    mensagem = (
        f"🔥 *{oferta['titulo']}*\n\n"
        f"❌ De: ~{preco_antigo_str}~\n"
        f"✅ *Por: {preco_atual_str}* _(-{desconto}% OFF)_"
        f"{linha_cupom}\n\n"
        f"🛒 *Link direto da oferta:* {oferta['link_afiliado']}\n\n"
        f"Quer receber mais anúncios de promoções como este? Entre na nossa comunidade do WhatsApp:\n"
        f"{LINK_GRUPO_WHATSAPP}"
    )
    return mensagem


def gerar_texto_cupom(cupom: dict) -> str:
    """
    Gera o disparo de cupom 100% decodificado (sem códigos como &#225; ou &#233;).
    """
    beneficio_limpo = html.unescape(cupom["beneficio"])
    regra_limpa = html.unescape(cupom["regra"])

    mensagem = (
        f"🎟️ *CUPOM {cupom['loja'].upper()} LIBERADO!*\n\n"
        f"🔥 *{beneficio_limpo}*\n"
        f"🏷️ Cupom: *{cupom['codigo']}*\n"
        f"📌 _{regra_limpa}_\n\n"
        f"🛒 *Use o cupom aqui:* {cupom['link_afiliado']}\n\n"
        f"Quer receber mais anúncios de promoções como este? Entre na nossa comunidade do WhatsApp:\n"
        f"{LINK_GRUPO_WHATSAPP}"
    )
    return mensagem


def gerar_texto_facebook(oferta: dict) -> str:
    preco_antigo_str = formatar_moeda(oferta["preco_original"])
    preco_atual_str = formatar_moeda(oferta["preco_atual"])
    desconto = oferta.get("desconto_pct", 0)
    return (
        f"🔥 {oferta['titulo']}\n\n"
        f"❌ De: {preco_antigo_str}\n"
        f"✅ Por: {preco_atual_str} (-{desconto}% OFF)\n\n"
        f"🛒 Link da oferta: {oferta['link_afiliado']}\n\n"
        f"Quer receber mais anúncios de promoções como este? Entre na nossa comunidade do WhatsApp:\n"
        f"{LINK_GRUPO_WHATSAPP}"
    )


def gerar_dados_pinterest(oferta: dict) -> dict:
    preco_antigo_str = formatar_moeda(oferta["preco_original"])
    preco_atual_str = formatar_moeda(oferta["preco_atual"])
    titulo_curto = oferta["titulo"][:70].strip()
    return {
        "titulo": f"🔥 {titulo_curto} ({preco_atual_str})"[:100],
        "descricao": (
            f"🔥 {oferta['titulo']}\n"
            f"❌ De: {preco_antigo_str}  ✅ Por: {preco_atual_str}\n"
            f"Quer receber mais anúncios de promoções como este? Entre na nossa comunidade do WhatsApp: "
            f"{LINK_GRUPO_WHATSAPP} #promocao #ofertas #desconto #achadinhos"
        )[:500],
        "link_destino": oferta["link_afiliado"],
    }


def gerar_texto_instagram(oferta: dict) -> str:
    preco_antigo_str = formatar_moeda(oferta["preco_original"])
    preco_atual_str = formatar_moeda(oferta["preco_atual"])
    desconto = oferta.get("desconto_pct", 0)
    return (
        f"🔥 {oferta['titulo']}\n\n"
        f"❌ De: {preco_antigo_str}\n"
        f"✅ Por: {preco_atual_str} (-{desconto}% OFF)\n\n"
        f"📲 Link direto da oferta liberado na nossa bio e no canal VIP do WhatsApp!\n\n"
        f"👉 Entre no canal pelo link da bio para garantir antes que o preço suba!\n\n"
        f"#promocao #achadinhos #desconto #ofertas #compras #cupom"
    )


def gerar_texto_cupom_instagram(cupom: dict) -> str:
    beneficio_limpo = html.unescape(cupom["beneficio"])
    regra_limpa = html.unescape(cupom["regra"])
    return (
        f"🎟️ CUPOM {cupom['loja'].upper()} LIBERADO!\n\n"
        f"🔥 {beneficio_limpo}\n"
        f"🏷️ Cupom: {cupom['codigo']}\n"
        f"📌 {regra_limpa}\n\n"
        f"📲 Link oficial para ativar o cupom liberado na nossa BIO e no canal VIP do WhatsApp!\n\n"
        f"👉 Acesse pelo link da bio e aproveite antes de esgotar!\n\n"
        f"#cupom #cupomdedesconto #promocao #achadinhos #ofertas #{cupom['slug_loja']}"
    )
