import json
import random
from urllib.parse import quote_plus
import requests
from config import (
    AMAZON_TAG,
    ML_AFFILIATE_ID,
    LOMADEE_SOURCE_ID,
    LOMADEE_APP_TOKEN,
    DESCONTO_MINIMO,
    HISTORICO_PATH,
)
from controle_repeticao import foi_enviado_recentemente

QUERIES_CAMPEAS = [
    "logitech",
    "hyperx",
    "jbl",
    "redragon",
    "kingston ssd",
    "monitor gamer",
    "headset gamer",
    "teclado mecanico",
    "mouse gamer",
    "air fryer",
    "samsung galaxy",
    "controle ps5 xbox",
    "corsair",
    "razer",
]


def carregar_historico() -> set:
    if not HISTORICO_PATH.exists():
        return set()
    try:
        dados = json.loads(HISTORICO_PATH.read_text(encoding="utf-8"))
        return set(dados)
    except Exception:
        return set()


def salvar_no_historico(id_oferta: str):
    historico = carregar_historico()
    historico.add(str(id_oferta))
    lista = list(historico)[-500:]
    HISTORICO_PATH.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")


def converter_link_lomadee(url_original: str) -> str | None:
    """
    Converte qualquer link de loja parceira (KaBuM, Magalu, Nike, AliExpress, etc.)
    em um link de afiliado seu automaticamente via API Oficial da Lomadee.
    """
    if not LOMADEE_SOURCE_ID or not LOMADEE_APP_TOKEN:
        return None
    try:
        api_url = f"https://api.lomadee.com/v2/{LOMADEE_APP_TOKEN}/deeplink/_create"
        params = {"sourceId": LOMADEE_SOURCE_ID, "url": url_original}
        resp = requests.get(api_url, params=params, timeout=8)
        if resp.status_code == 200:
            deeplinks = resp.json().get("deeplinks") or []
            if deeplinks and deeplinks[0].get("deeplink"):
                return deeplinks[0]["deeplink"]
    except Exception:
        pass
    return None


def gerar_link_afiliado(titulo_produto: str, id_produto: str = "", product_slug: str = "") -> str:
    """
    Gera o link de afiliado:
    1. Se tiver id/slug da KaBuM e Lomadee configurada, gera o link DIRETO do produto com UTM rastreada.
    2. Caso contrário, gera comissão no Mercado Livre / Amazon.
    """
    if id_produto and product_slug:
        # Link direto para a página do produto na KaBuM com rastreamento da Lomadee
        utm_params = (
            f"?utm_source=lomadee&utm_medium=link_generator"
            f"&utm_campaign=9902768e-112d-4f43-abde-d0ab828996aa_e198615b-4c17-4180-b06f-43376f162714"
        )
        return f"https://www.kabum.com.br/produto/{id_produto}/{product_slug}{utm_params}"

    palavras = titulo_produto.replace(",", " ").replace("-", " ").split()
    termo_limpo = " ".join(palavras[:6])

    if ML_AFFILIATE_ID and AMAZON_TAG == "seu-id-20":
        slug = "-".join(palavras[:6]).lower()
        return f"https://lista.mercadolivre.com.br/{quote_plus(slug)}?{ML_AFFILIATE_ID}"

    return f"https://www.amazon.com.br/s?k={quote_plus(termo_limpo)}&tag={AMAZON_TAG}"


def buscar_ofertas_por_termo(termo: str) -> list[dict]:
    """
    Consulta ofertas reais em tempo real para um termo/marca específica,
    extraindo foto de alta definição, preço original, preço em oferta e % de desconto.
    """
    ofertas = []
    url = "https://servicespub.prod.api.aws.grupokabum.com.br/catalog/v2/products"
    params = {"query": termo, "page_number": 1, "page_size": 25}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=12)
        if resp.status_code != 200:
            return []

        itens = resp.json().get("data", [])
        for item in itens:
            attr = item.get("attributes") or {}
            offer = attr.get("offer") or {}

            preco_cheio = float(attr.get("old_price") or attr.get("price") or 0)
            preco_atual = float(
                offer.get("price_with_discount")
                or attr.get("price_with_discount")
                or 0
            )

            if preco_atual <= 0 or preco_cheio <= preco_atual:
                continue

            desconto_pct = int(round(((preco_cheio - preco_atual) / preco_cheio) * 100))
            if desconto_pct < DESCONTO_MINIMO:
                continue

            fotos = (attr.get("photos") or {}).get("g") or []
            if not fotos:
                continue

            titulo = attr.get("title", "").strip()
            product_slug = attr.get("product_link", "")
            qtd_parcelas = min(10, max(1, int(preco_atual // 35)))
            valor_parcela = round(preco_atual / qtd_parcelas, 2)

            ofertas.append({
                "id": f"PROD_{item.get('id')}",
                "loja": "Oferta Verificada",
                "titulo": titulo,
                "preco_original": preco_cheio,
                "preco_atual": preco_atual,
                "desconto_pct": desconto_pct,
                "parcelas_qtd": qtd_parcelas,
                "parcelas_valor": valor_parcela,
                "imagem_url": fotos[0],
                "link_afiliado": gerar_link_afiliado(titulo, str(item.get("id", "")), product_slug),
            })
    except Exception as e:
        print(f"Aviso na busca ({termo}): {e}")

    return ofertas


def encontrar_melhor_oferta_inédita() -> dict | None:
    """
    Sorteia marcas/termos campeões de venda, busca descontos reais ao vivo,
    filtra os produtos que já foram postados e retorna o maior desconto encontrado.
    """
    historico = carregar_historico()
    termos_embaralhados = random.sample(QUERIES_CAMPEAS, k=min(4, len(QUERIES_CAMPEAS)))

    candidatas = []
    for termo in termos_embaralhados:
        encontradas = buscar_ofertas_por_termo(termo)
        for of in encontradas:
            if of["id"] in historico:
                continue
            if foi_enviado_recentemente(of["id"]) or foi_enviado_recentemente(of["link_afiliado"]):
                continue
            candidatas.append(of)
        if len(candidatas) >= 5:
            break

    if not candidatas:
        return None

    candidatas.sort(key=lambda x: x["desconto_pct"], reverse=True)
    return candidatas[0]
