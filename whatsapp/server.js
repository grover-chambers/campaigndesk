const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const express = require('express');
const cors = require('cors');
const qrcode = require('qrcode');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

let qrCodeData = null;
let clientReady = false;
let clientInfo = null;

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: './wa_session' }),
    puppeteer: {
        headless: true,
        executablePath: '/usr/bin/chromium',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--single-process',
            '--disable-gpu'
        ]
    }
});

client.on('qr', async (qr) => {
    console.log('QR received — scan with WhatsApp');
    qrCodeData = await qrcode.toDataURL(qr);
    clientReady = false;
});

client.on('ready', () => {
    console.log('WhatsApp client ready!');
    clientReady = true;
    qrCodeData = null;
    clientInfo = client.info;
});

client.on('authenticated', () => {
    console.log('WhatsApp authenticated');
});

client.on('auth_failure', (msg) => {
    console.error('Auth failure:', msg);
    clientReady = false;
});

client.on('disconnected', (reason) => {
    console.log('WhatsApp disconnected:', reason);
    clientReady = false;
    clientInfo = null;
});

client.initialize();

// ── Routes ──

app.get('/status', (req, res) => {
    res.json({
        ready: clientReady,
        hasQR: !!qrCodeData,
        phone: clientInfo ? clientInfo.wid.user : null,
        name: clientInfo ? clientInfo.pushname : null
    });
});

app.get('/qr', (req, res) => {
    if (clientReady) {
        return res.json({ ready: true, message: 'Already connected' });
    }
    if (!qrCodeData) {
        return res.json({ ready: false, qr: null, message: 'Generating QR, please wait...' });
    }
    res.json({ ready: false, qr: qrCodeData });
});

app.get('/groups', async (req, res) => {
    if (!clientReady) return res.status(503).json({ error: 'WhatsApp not connected' });
    try {
        const chats = await client.getChats();
        const groups = chats
            .filter(c => c.isGroup)
            .map(g => ({
                id: g.id._serialized,
                name: g.name,
                memberCount: g.participants ? g.participants.length : 0,
                timestamp: g.timestamp
            }))
            .sort((a, b) => b.timestamp - a.timestamp);
        res.json({ groups });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.post('/send-message', async (req, res) => {
    if (!clientReady) return res.status(503).json({ error: 'WhatsApp not connected' });
    const { to, message } = req.body;
    if (!to || !message) return res.status(400).json({ error: 'to and message required' });
    try {
        await client.sendMessage(to, message);
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.post('/send-pdf', async (req, res) => {
    if (!clientReady) return res.status(503).json({ error: 'WhatsApp not connected' });
    const { to, pdfPath, caption } = req.body;
    if (!to || !pdfPath) return res.status(400).json({ error: 'to and pdfPath required' });
    if (!fs.existsSync(pdfPath)) return res.status(404).json({ error: 'PDF file not found' });
    try {
        const media = MessageMedia.fromFilePath(pdfPath);
        await client.sendMessage(to, media, { caption: caption || 'Meeting Minutes' });
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.post('/logout', async (req, res) => {
    try {
        await client.logout();
        clientReady = false;
        clientInfo = null;
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

const PORT = 3001;
app.listen(PORT, '127.0.0.1', () => {
    console.log(`WhatsApp service running on port ${PORT}`);
});
