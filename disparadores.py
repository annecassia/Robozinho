import base64
import os
from pathlib import Path
import shutil
import subprocess
import requests
from config import (
    BASE_DIR,
    OUTPUT_DIR,
    DADOS_DIR,
    WHATSAPP_ATIVO,
    GREEN_API_INSTANCE_ID,
    GREEN_API_TOKEN,
    WHATSAPP_GROUP_ID,
    FACEBOOK_ATIVO,
    FACEBOOK_PAGE_ID,
    FACEBOOK_PAGE_ACCESS_TOKEN,
    PINTEREST_ATIVO,
    PINTEREST_ACCESS_TOKEN,
    PINTEREST_BOARD_ID,
    INSTAGRAM_ATIVO,
    INSTAGRAM_ACCOUNT_ID,
    INSTAGRAM_ACCESS_TOKEN,
)

SESSAO_WA_LOCAL = DADOS_DIR / "sessao_whatsapp" / "creds.json"


def disparar_whatsapp(caminho_imagem: Path, mensagem_whatsapp: str) -> bool:
    """
    Envia a 1ª foto original do anúncio + texto para o seu Canal/Grupo do WhatsApp.
    Funciona direto pelo QR Code Local (whatsapp_sender.js) OU via Green-API.
    """
    # 1. Se o WhatsApp já estiver conectado via QR Code local (Node/Baileys)
    if SESSAO_WA_LOCAL.exists():
        arq_legenda = OUTPUT_DIR / "temp_legenda_wa.txt"
        arq_legenda.write_text(mensagem_whatsapp, encoding="utf-8")
        try:
            res = subprocess.run(
                ["node", str(BASE_DIR / "whatsapp_sender.js"), "--enviar-oferta", str(caminho_imagem), str(arq_legenda)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=35,
            )
            print(res.stdout.strip())
            return res.returncode == 0
        except Exception as e:
            print(f"   [WhatsApp Local] ❌ Erro ao enviar: {e}")
            return False

    # 2. Caso contrário, tenta via Green-API se configurado no .env
    if not WHATSAPP_ATIVO or not GREEN_API_INSTANCE_ID or not GREEN_API_TOKEN:
        print("   [WhatsApp] ⚠️ Ainda não conectado. Rode: node whatsapp_sender.js --conectar")
        return False

    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE_ID}/sendFileByUpload/{GREEN_API_TOKEN}"
    try:
        with open(caminho_imagem, "rb") as img_file:
            payload = {"chatId": WHATSAPP_GROUP_ID, "caption": mensagem_whatsapp}
            files = {"file": (caminho_imagem.name, img_file, "image/jpeg")}
            resp = requests.post(url, data=payload, files=files, timeout=20)
            if resp.status_code == 200:
                print("   [WhatsApp] ✅ Oferta disparada com sucesso!")
                return True
            print(f"   [WhatsApp] ⚠️ Erro da API ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"   [WhatsApp] ❌ Falha ao enviar: {e}")
    return False


def disparar_texto_whatsapp(mensagem_texto: str) -> bool:
    """Envia mensagem de texto (Disparo de Cupom) no Canal/Grupo do WhatsApp."""
    if SESSAO_WA_LOCAL.exists():
        arq_cupom = OUTPUT_DIR / "temp_cupom_wa.txt"
        arq_cupom.write_text(mensagem_texto, encoding="utf-8")
        try:
            res = subprocess.run(
                ["node", str(BASE_DIR / "whatsapp_sender.js"), "--enviar-texto", "", str(arq_cupom)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=35,
            )
            print(res.stdout.strip())
            return res.returncode == 0
        except Exception as e:
            print(f"   [WhatsApp Cupom] ❌ Erro ao enviar: {e}")
            return False

    if not WHATSAPP_ATIVO or not GREEN_API_INSTANCE_ID or not GREEN_API_TOKEN:
        return False

    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE_ID}/sendMessage/{GREEN_API_TOKEN}"
    try:
        payload = {"chatId": WHATSAPP_GROUP_ID, "message": mensagem_texto}
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            print("   [WhatsApp Cupom] ✅ Cupom disparado com sucesso!")
            return True
    except Exception as e:
        print(f"   [WhatsApp Cupom] ❌ Falha ao enviar cupom: {e}")
    return False


def disparar_facebook(caminho_imagem: Path, mensagem_facebook: str) -> bool:
    """Publica a 1ª foto original do anúncio + legenda na Página do Facebook."""
    if not FACEBOOK_ATIVO or not FACEBOOK_PAGE_ID or not FACEBOOK_PAGE_ACCESS_TOKEN:
        return False

    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/photos"
    try:
        with open(caminho_imagem, "rb") as img_file:
            payload = {
                "caption": mensagem_facebook,
                "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
            }
            files = {"source": (caminho_imagem.name, img_file, "image/jpeg")}
            resp = requests.post(url, data=payload, files=files, timeout=25)
            if resp.status_code in (200, 201):
                print(f"   [Facebook] ✅ Post publicado automaticamente na Página! (ID: {resp.json().get('id')})")
                return True
            print(f"   [Facebook] ⚠️ Resposta da API ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"   [Facebook] ❌ Falha ao postar: {e}")
    return False


def hospedar_imagem_para_meta(caminho_imagem: Path, nome_arquivo: str = "ig_upload.jpg") -> str | None:
    """Copia a imagem local para o site e publica no Surge para o Instagram baixar sem bloqueio."""
    try:
        site_dir = BASE_DIR / "site_annewealth"
        destino = site_dir / nome_arquivo
        shutil.copyfile(caminho_imagem, destino)
        env = os.environ.copy()
        env["SURGE_TOKEN"] = "1ce543cfb21cae803b0957b98d2f4447"
        subprocess.run(
            ["cmd.exe", "/c", "npx.cmd", "surge", str(site_dir), "annewealth.surge.sh"],
            env=env,
            capture_output=True,
            timeout=25,
        )
        return f"https://annewealth.surge.sh/{nome_arquivo}"
    except Exception as e:
        print(f"   [Instagram] Aviso ao hospedar imagem: {e}")
        return None


def disparar_instagram(origem_imagem, legenda_instagram: str) -> bool:
    """
    Publica no feed do Instagram Business/Creator (@annecassialmeida).
    Aceita tanto um Path local (hospeda automaticamente) quanto uma URL pública HTTPS.
    """
    if not INSTAGRAM_ATIVO or not INSTAGRAM_ACCOUNT_ID or not INSTAGRAM_ACCESS_TOKEN:
        return False

    url_final = None
    if isinstance(origem_imagem, Path) or (isinstance(origem_imagem, str) and Path(origem_imagem).exists()):
        url_final = hospedar_imagem_para_meta(Path(origem_imagem))
    elif isinstance(origem_imagem, str) and origem_imagem.startswith("http"):
        url_final = origem_imagem

    if not url_final:
        print("   [Instagram] ⚠️ Imagem não disponível para envio ao Instagram.")
        return False

    url_container = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    try:
        # 1. Cria o container de mídia no Instagram
        params_container = {
            "image_url": url_final,
            "caption": legenda_instagram,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }
        resp1 = requests.post(url_container, data=params_container, timeout=25)
        if resp1.status_code not in (200, 201):
            print(f"   [Instagram] ⚠️ Erro container ({resp1.status_code}): {resp1.text}")
            return False

        container_id = resp1.json().get("id")
        if not container_id:
            return False

        # 2. Publica a mídia no feed
        url_publish = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        params_publish = {
            "creation_id": container_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }
        resp2 = requests.post(url_publish, data=params_publish, timeout=25)
        if resp2.status_code in (200, 201):
            print(f"   [Instagram] ✅ Post publicado no feed @loja.annes! (ID: {resp2.json().get('id')})")
            return True
        print(f"   [Instagram] ⚠️ Erro publicação ({resp2.status_code}): {resp2.text}")
    except Exception as e:
        print(f"   [Instagram] ❌ Falha ao postar no Instagram: {e}")
    return False


def disparar_pinterest(caminho_imagem: Path, dados_pinterest: dict) -> bool:
    """Cria um Pin automático no Pinterest Business usando a 1ª foto original do anúncio."""
    if not PINTEREST_ATIVO or not PINTEREST_ACCESS_TOKEN or not PINTEREST_BOARD_ID:
        return False

    url = "https://api.pinterest.com/v5/pins"
    try:
        img_b64 = base64.b64encode(caminho_imagem.read_bytes()).decode("utf-8")
        headers = {
            "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "board_id": PINTEREST_BOARD_ID,
            "title": dados_pinterest["titulo"],
            "description": dados_pinterest["descricao"],
            "link": dados_pinterest["link_destino"],
            "media_source": {
                "source_type": "image_base64",
                "content_type": "image/jpeg",
                "data": img_b64,
            },
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code in (200, 201):
            print("   [Pinterest] ✅ Pin publicado automaticamente com seu link de afiliado!")
            return True
    except Exception as e:
        print(f"   [Pinterest] ❌ Falha ao criar Pin: {e}")
    return False


def salvar_preview_local(
    oferta: dict,
    caminho_imagem: Path,
    txt_whatsapp: str,
    txt_facebook: str,
    dados_pinterest: dict,
    txt_cupom: str = "",
):
    """Salva os textos prontos em output/ultima_oferta_pronta.txt para conferência."""
    conteudo = (
        f"======================================================================\n"
        f"1ª FOTO ORIGINAL DO ANÚNCIO SALVA EM:\n"
        f"{caminho_imagem}\n"
        f"======================================================================\n\n"
        f"--- [WHATSAPP] MENSAGEM DA OFERTA ---\n"
        f"{txt_whatsapp}\n\n"
        f"--- [FACEBOOK] MENSAGEM DA OFERTA ---\n"
        f"{txt_facebook}\n\n"
        f"--- [PINTEREST] DADOS DO PIN ---\n"
        f"Título: {dados_pinterest['titulo']}\n"
        f"Descrição:\n{dados_pinterest['descricao']}\n"
        f"Link de Destino: {dados_pinterest['link_destino']}\n"
    )
    if txt_cupom:
        conteudo += (
            f"\n======================================================================\n"
            f"--- [BÔNUS] DISPARO DE CUPOM DE DESCONTO ---\n"
            f"======================================================================\n"
            f"{txt_cupom}\n"
        )
    arquivo_txt = OUTPUT_DIR / "ultima_oferta_pronta.txt"
    arquivo_txt.write_text(conteudo, encoding="utf-8")
    return arquivo_txt
