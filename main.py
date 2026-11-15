import sys
import time
from cacador_ofertas import encontrar_melhor_oferta_inédita, salvar_no_historico
from cacador_cupons import encontrar_cupom_inedito
from formatador_mensagens import (
    gerar_texto_whatsapp,
    gerar_texto_facebook,
    gerar_dados_pinterest,
    gerar_texto_instagram,
    gerar_texto_cupom_instagram,
    gerar_texto_cupom,
)
from gerador_imagem import baixar_primeira_foto_anuncio, obter_logo_loja_cupom
from disparadores import (
    disparar_whatsapp,
    disparar_facebook,
    disparar_instagram,
    disparar_pinterest,
    salvar_preview_local,
)
from controle_repeticao import registrar_envio

# Intervalo padrão humanizado entre a postagem da oferta e do cupom (em segundos)
INTERVALO_ENTRE_POSTAGENS = 90  # 1 minuto e meio


def executar_ciclo_robo(delay_entre_posts: int = INTERVALO_ENTRE_POSTAGENS):
    print("\n" + "=" * 70)
    print("🤖 INICIANDO VARREDURA DO ROBÔ (OFERTAS + CUPONS COM LOGO)...")
    print("=" * 70)

    oferta = encontrar_melhor_oferta_inédita()
    if not oferta:
        print("⚠️ Nenhuma oferta nova acima do desconto mínimo encontrada neste ciclo.")
    else:
        print(f"✅ Oferta Encontrada: {oferta['titulo']}")
        print(
            f"💰 De R$ {oferta['preco_original']:.2f} por R$ {oferta['preco_atual']:.2f} "
            f"(-{oferta['desconto_pct']}% OFF)"
        )

        # 1. Baixa diretamente a PRIMEIRA foto original do anúncio
        print("\n📸 Baixando a 1ª foto original do anúncio...")
        caminho_foto = baixar_primeira_foto_anuncio(oferta)
        print(f"   Foto original salva em: {caminho_foto}")

        # 2. Formata as mensagens
        txt_whatsapp = gerar_texto_whatsapp(oferta)
        txt_facebook = gerar_texto_facebook(oferta)
        txt_instagram = gerar_texto_instagram(oferta)
        dados_pinterest = gerar_dados_pinterest(oferta)

        # 3. Salva preview local
        arquivo_preview = salvar_preview_local(
            oferta, caminho_foto, txt_whatsapp, txt_facebook, dados_pinterest
        )
        print(f"📄 Mensagem salva em: {arquivo_preview}")

        # 4. Dispara a Oferta nos canais
        print("\n🚀 Disparando Oferta nas plataformas...")
        disparar_whatsapp(caminho_foto, txt_whatsapp)
        disparar_facebook(caminho_foto, txt_facebook)
        disparar_instagram(caminho_foto, txt_instagram)
        disparar_pinterest(caminho_foto, dados_pinterest)

        # Registra no histórico permanente e na janela de 1 hora anti-repetição
        salvar_no_historico(oferta["id"])
        registrar_envio(oferta["link_afiliado"])
        registrar_envio(oferta["id"])

    # 5. Busca um cupom inédito (com rotação de loja e sem repetir em 1 hora)
    cupom = encontrar_cupom_inedito()
    if cupom:
        txt_cupom = gerar_texto_cupom(cupom)
        txt_cupom_ig = gerar_texto_cupom_instagram(cupom)
        caminho_logo_cupom = obter_logo_loja_cupom(cupom)
        print(
            f"\n🎟️ Cupom Inédito Encontrado [{cupom['loja']}]: {cupom['beneficio']} "
            f"(Código: {cupom['codigo']} | Logo: {caminho_logo_cupom.name})"
        )

        # Aguarda 1 a 2 minutos para parecer 100% humano e não floodar os canais
        if delay_entre_posts > 0 and oferta:
            print(f"\n⏳ Aguardando {delay_entre_posts} segundos (intervalo inteligente) antes de disparar o cupom...")
            time.sleep(delay_entre_posts)

        print(f"\n🎟️ Disparando Cupom da {cupom['loja']}...")
        disparar_whatsapp(caminho_logo_cupom, txt_cupom)
        disparar_facebook(caminho_logo_cupom, txt_cupom)
        disparar_instagram(caminho_logo_cupom, txt_cupom_ig)

        # Registra no histórico permanente e na janela de 1 hora
        salvar_no_historico(cupom["id"])
        registrar_envio(cupom["link_afiliado"])
        registrar_envio(cupom["beneficio"])
        registrar_envio(cupom["id"])
    else:
        print("\nℹ️ Nenhum cupom inédito disponível no momento (rotação/janela de 1h ativa).")

    print("\n✨ Ciclo concluído com sucesso!")


if __name__ == "__main__":
    sem_delay = "--sem-delay" in sys.argv
    delay_aplicado = 0 if sem_delay else INTERVALO_ENTRE_POSTAGENS

    if "--loop" in sys.argv:
        intervalo_minutos = 30
        print(f"🔄 Modo Contínuo Ativado! Rodando a cada {intervalo_minutos} minutos...")
        while True:
            executar_ciclo_robo(delay_entre_posts=delay_aplicado)
            print(f"\n⏳ Aguardando {intervalo_minutos} minutos até a próxima busca...")
            time.sleep(intervalo_minutos * 60)
    else:
        executar_ciclo_robo(delay_entre_posts=delay_aplicado)
