import html
import json
import re
from urllib.parse import urlparse
import requests
from config import AMAZON_TAG, ML_AFFILIATE_ID, SHOPEE_AFFILIATE_PARAMS, LOMADEE_APP_TOKEN, LOMADEE_SOURCE_ID, DADOS_DIR
from cacador_ofertas import carregar_historico
from gerador_imagem import detectar_slug_loja
from controle_repeticao import foi_enviado_recentemente, obter_ultima_loja_cupom, registrar_loja_cupom

CUPONS_MANUAIS_PATH = DADOS_DIR / "cupons_ativos.json"

NOMES_LOJA_POR_SLUG = {
    "shopee": "Shopee",
    "mercadolivre": "Mercado Livre",
    "amazon": "Amazon Brasil",
    "kabum": "KaBuM!",
    "magalu": "Magalu",
    "aliexpress": "AliExpress",
    "drogasmil": "Drogasmil",
    "pcyes": "PCYES Gamer",
    "sawary": "Sawary Jeans",
    "pneustore": "PneuStore",
}


def link_afiliado_por_slug(slug: str) -> str:
    """Retorna o seu link de afiliado correspondente à loja detectada no cupom."""
    if slug == "mercadolivre" and ML_AFFILIATE_ID:
        return f"https://www.mercadolivre.com.br/cupons?{ML_AFFILIATE_ID}"
    if slug == "shopee":
        if SHOPEE_AFFILIATE_PARAMS:
            return f"https://shopee.com.br/m/cupons-diarios?{SHOPEE_AFFILIATE_PARAMS}"
        return "https://shopee.com.br/m/cupons-diarios"
    if slug == "amazon":
        return f"https://www.amazon.com.br/coupons?tag={AMAZON_TAG}"
    return f"https://www.mercadolivre.com.br/cupons?{ML_AFFILIATE_ID}"


def buscar_cupons_lomadee() -> list[dict]:
    """
    Busca cupons e campanhas promocionais oficiais ativas na API oficial da Lomadee,
    já vinculando os links curtos do seu canal (Anne Cássia).
    """
    if not LOMADEE_APP_TOKEN:
        return []

    headers = {"x-api-key": LOMADEE_APP_TOKEN}
    url = "https://api.lomadee.com.br/affiliate/campaigns?limit=30"
    cupons = []

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []

        dados = resp.json().get("data", [])
        for c in dados:
            link = None
            for ch in c.get("channels", []):
                # Procura o link gerado para o canal Anne Cássia (19875024...)
                if ch.get("id") == LOMADEE_SOURCE_ID and ch.get("shortUrls"):
                    link = ch["shortUrls"][0]
                    break
            # Fallback para o primeiro canal disponível se não achar o canal exato
            if not link:
                for ch in c.get("channels", []):
                    if ch.get("shortUrls"):
                        link = ch["shortUrls"][0]
                        break

            if not link:
                continue

            # Nome amigável da loja a partir da URL
            url_loja = c.get("url", "")
            netloc = urlparse(url_loja).netloc.replace("www.", "").split(".")[0]
            nome_loja = netloc.capitalize()
            if "drogasmil" in netloc: nome_loja = "Drogasmil"
            elif "pcyes" in netloc: nome_loja = "PCYES"
            elif "motobr" in netloc: nome_loja = "Moto BR"
            elif "speedmax" in netloc: nome_loja = "SpeedMax"
            elif "sawary" in netloc: nome_loja = "Sawary"
            elif "pneustore" in netloc: nome_loja = "PneuStore"
            elif "bauducco" in netloc: nome_loja = "Bauducco"
            elif "carraro" in netloc: nome_loja = "Carraro"

            slug = detectar_slug_loja(f"{nome_loja} {c.get('name', '')}")
            codigo = c.get("code") or "ATIVAR NO LINK"

            cupons.append({
                "id": f"LMD_{c.get('id')}",
                "slug_loja": slug,
                "loja": nome_loja,
                "codigo": codigo,
                "beneficio": c.get("name", "Promoção Especial da Loja").strip(),
                "regra": "Válido na loja oficial através do link verificado Anne Wealth.",
                "link_afiliado": link,
            })
    except Exception as e:
        print(f"   [Lomadee Cupons] Aviso ao buscar campanhas: {e}")

    return cupons


def buscar_cupons_ao_vivo() -> list[dict]:
    """
    Busca cupons em tempo real de todas as fontes:
    1. Campanhas e Cupons Oficiais da Lomadee (Drogasmil, PCYES, Sawary, Moto BR, etc.)
    2. Cupons Oficiais Mercado Livre, Shopee e Amazon
    """
    cupons = []

    # 1. Puxa primeiro da API Oficial da Lomadee (máxima confiabilidade e variedade)
    cupons_lmd = buscar_cupons_lomadee()
    cupons.extend(cupons_lmd)

    # 2. Puxa os cupons dos gigantes (Shopee, Mercado Livre, Amazon)
    cupons_base = [
        {
            "id": "CUPOM_MELI_DESCONTO_FULL",
            "slug_loja": "mercadolivre",
            "loja": "Mercado Livre",
            "codigo": "MELI15OFF",
            "beneficio": "Até 20% OFF na Central de Cupons do Mercado Livre (Envio Full)",
            "regra": "Ative o cupom na página do Mercado Livre antes de finalizar.",
            "link_afiliado": link_afiliado_por_slug("mercadolivre"),
        },
        {
            "id": "CUPOM_SHOPEE_DIARIOS_FRETE",
            "slug_loja": "shopee",
            "loja": "Shopee",
            "codigo": "ATIVAR NO LINK",
            "beneficio": "Cupons Diários da Shopee + Cupons de Frete Grátis",
            "regra": "Válido no App da Shopee em Lojas Oficiais selecionadas.",
            "link_afiliado": link_afiliado_por_slug("shopee"),
        },
        {
            "id": "CUPOM_AMZ_CENTRAL_DESCONTOS",
            "slug_loja": "amazon",
            "loja": "Amazon Brasil",
            "codigo": "APLICAR NA PÁGINA",
            "beneficio": "Até 30% OFF na Central Oficial de Cupons da Amazon",
            "regra": "Basta clicar em 'Aplicar Cupom' diretamente na página do produto.",
            "link_afiliado": link_afiliado_por_slug("amazon"),
        },
    ]
    cupons.extend(cupons_base)

    return cupons


def encontrar_cupom_inedito() -> dict | None:
    """
    Retorna um cupom inédito com verificação estrita:
    1. Não repete a mesma loja em seguida (Rotação de Lojas).
    2. Não repete o mesmo link ou benefício se foi enviado na última 1 hora.
    3. Não repete cupom já arquivado no histórico geral.
    """
    historico = carregar_historico()
    todos_cupons = buscar_cupons_ao_vivo()
    ultima_loja = obter_ultima_loja_cupom().strip().lower()

    candidatos_outra_loja = []
    candidatos_gerais = []

    for cupom in todos_cupons:
        # Filtro 1: Histórico Geral
        if cupom["id"] in historico:
            continue

        # Filtro 2: Janela de 1 hora (Não repete o mesmo link nem mesma mensagem em 1 hora)
        if foi_enviado_recentemente(cupom["link_afiliado"]):
            continue
        if foi_enviado_recentemente(cupom["beneficio"]):
            continue

        # Filtro 3: Rotação de Loja (se for de loja diferente da última, tem prioridade máxima)
        loja_atual = cupom["loja"].strip().lower()
        if ultima_loja and loja_atual == ultima_loja:
            candidatos_gerais.append(cupom)
        else:
            candidatos_outra_loja.append(cupom)

    # Escolhe preferencialmente de outra loja para garantir variedade
    escolhido = None
    if candidatos_outra_loja:
        escolhido = candidatos_outra_loja[0]
    elif candidatos_gerais:
        escolhido = candidatos_gerais[0]

    if escolhido:
        registrar_loja_cupom(escolhido["loja"])

    return escolhido
