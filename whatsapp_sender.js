import makeWASocket, {
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} from '@whiskeysockets/baileys';
import QRCode from 'qrcode';
import pino from 'pino';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SESSAO_DIR = path.join(__dirname, 'dados', 'sessao_whatsapp');
const QR_FILE = path.join(__dirname, 'CONECTAR_WHATSAPP_QRCODE.png');

// Código extraído do seu link: https://whatsapp.com/channel/0029Vb94NjPIyPtZOVnlwA3a
const CODIGO_CANAL = '0029Vb94NjPIyPtZOVnlwA3a';

const modo = process.argv[2] || '--conectar';
const caminhoImagem = process.argv[3] || '';
const caminhoTexto = process.argv[4] || '';

async function iniciarWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(SESSAO_DIR);
    const { version } = await fetchLatestBaileysVersion();

    const sock = makeWASocket({
        version,
        logger: pino({ level: 'silent' }),
        auth: state,
        printQRInTerminal: false,
        browser: ['Robo Ofertas VIP', 'Chrome', '120.0.0']
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            await QRCode.toFile(QR_FILE, qr, { width: 480, margin: 2 });
            console.log('\n================================================================');
            console.log('📱 QR CODE GERADO COM SUCESSO!');
            console.log('👉 Clique no arquivo: CONECTAR_WHATSAPP_QRCODE.png (aqui na pasta)');
            console.log('👉 No WhatsApp do seu celular: Aparelhos Conectados -> Conectar Aparelho');
            console.log('⏳ Aguardando você escanear o QR Code...');
            console.log('================================================================\n');
        }

        if (connection === 'close') {
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const deveReconectar = statusCode !== DisconnectReason.loggedOut;
            if (deveReconectar) {
                iniciarWhatsApp();
            } else {
                console.log('❌ Sessão desconectada pelo celular.');
                process.exit(1);
            }
        } else if (connection === 'open') {
            console.log('✅ WHATSAPP CONECTADO COM SUCESSO!');
            if (fs.existsSync(QR_FILE)) {
                try { fs.unlinkSync(QR_FILE); } catch (e) {}
            }

            try {
                let destinoJid = '120363412439180579@newsletter';
                if (typeof sock.newsletterMetadata === 'function') {
                    try {
                        const meta = await sock.newsletterMetadata('invite', CODIGO_CANAL);
                        if (meta && meta.id) {
                            destinoJid = meta.id;
                        }
                    } catch (errCanal) {}
                }

                if (modo === '--enviar-oferta' && caminhoImagem && caminhoTexto && destinoJid) {
                    const legenda = fs.readFileSync(caminhoTexto, 'utf-8');
                    const bufferImg = fs.readFileSync(caminhoImagem);

                    await sock.sendMessage(destinoJid, {
                        image: bufferImg,
                        caption: legenda
                    });
                    console.log('🚀 OFERTA ENVIADA COM SUCESSO NO SEU CANAL DO WHATSAPP!');
                } else if (modo === '--enviar-texto' && caminhoTexto && destinoJid) {
                    const texto = fs.readFileSync(caminhoTexto, 'utf-8');
                    await sock.sendMessage(destinoJid, { text: texto });
                    console.log('🚀 CUPOM ENVIADO COM SUCESSO NO SEU CANAL DO WHATSAPP!');
                } else if (modo === '--conectar') {
                    console.log('🎉 WhatsApp pareado com sucesso! (Nenhuma mensagem de status foi enviada ao canal).');
                }
            } catch (errEnvio) {
                console.error('❌ Erro durante envio:', errEnvio.message);
            }

            setTimeout(() => process.exit(0), 3000);
        }
    });
}

iniciarWhatsApp();
