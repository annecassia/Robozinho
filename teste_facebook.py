"""Teste isolado: posta a última oferta encontrada SOMENTE na Página do Facebook."""
from cacador_ofertas import encontrar_melhor_oferta_inédita, salvar_no_historico
from formatador_mensagens import gerar_texto_facebook
from gerador_imagem import baixar_primeira_foto_anuncio
from disparadores import disparar_facebook

oferta = encontrar_melhor_oferta_inédita()
if not oferta:
    print("Nenhuma oferta nova encontrada.")
else:
    print(f"Oferta: {oferta['titulo']}")
    foto = baixar_primeira_foto_anuncio(oferta)
    texto = gerar_texto_facebook(oferta)
    if disparar_facebook(foto, texto):
        salvar_no_historico(oferta["id"])
