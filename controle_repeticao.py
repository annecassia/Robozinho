import json
import time
from pathlib import Path
from config import DADOS_DIR

REGISTRO_PATH = DADOS_DIR / "registro_envios_recentes.json"
ESTADO_LOJA_PATH = DADOS_DIR / "ultimo_estado_loja.json"

JANELA_EXPIRACAO_PADRAO = 3600  # 1 hora em segundos


def _carregar_registro() -> dict[str, float]:
    """Carrega o mapa de identificadores/links e seus timestamps de envio."""
    if not REGISTRO_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRO_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _salvar_registro(dados: dict[str, float]):
    """Salva o mapa limpo no disco."""
    REGISTRO_PATH.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def limpar_registros_expirados(janela_segundos: int = JANELA_EXPIRACAO_PADRAO) -> dict[str, float]:
    """
    Remove do arquivo todos os registros que foram enviados há mais de 1 hora (ou janela definida).
    Quando bate 1 hora, apaga esse registro automaticamente.
    """
    agora = time.time()
    dados = _carregar_registro()
    dados_validos = {
        item: ts for item, ts in dados.items() if (agora - ts) < janela_segundos
    }
    if len(dados_validos) != len(dados):
        _salvar_registro(dados_validos)
    return dados_validos


def foi_enviado_recentemente(identificador: str, janela_segundos: int = JANELA_EXPIRACAO_PADRAO) -> bool:
    """
    Verifica se o link, ID ou título já foi enviado na última 1 hora.
    Se já tiver passado de 1 hora, o registro é apagado e ele volta a ser permitido.
    """
    if not identificador:
        return False
    dados_ativos = limpar_registros_expirados(janela_segundos)
    item_normalizado = identificador.strip().lower()
    return item_normalizado in dados_ativos


def registrar_envio(identificador: str):
    """
    Registra que o link/ID/mensagem foi enviado no timestamp atual.
    Esse registro ficará protegido por 1 hora.
    """
    if not identificador:
        return
    dados = limpar_registros_expirados()
    item_normalizado = identificador.strip().lower()
    dados[item_normalizado] = time.time()
    _salvar_registro(dados)


def obter_ultima_loja_cupom() -> str:
    """Retorna o nome da última loja que teve cupom disparado para rotação."""
    if not ESTADO_LOJA_PATH.exists():
        return ""
    try:
        dados = json.loads(ESTADO_LOJA_PATH.read_text(encoding="utf-8"))
        return dados.get("ultima_loja", "")
    except Exception:
        return ""


def registrar_loja_cupom(loja: str):
    """Registra a loja do último cupom disparado para garantir alternância."""
    ESTADO_LOJA_PATH.write_text(
        json.dumps({"ultima_loja": loja.strip()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
