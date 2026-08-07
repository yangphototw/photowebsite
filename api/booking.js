const GOOGLE_SHEETS_URL = 'https://script.google.com/macros/s/AKfycbwr64qsLJgqajMP_xwu5Z17uJmZAp21guLW-I_0dTH_3LKb9IGbIuiZ2X2w4Or7TLM4CA/exec';

const asText = (value, limit) => typeof value === 'string' ? value.trim().slice(0, limit) : '';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ message: 'Method not allowed.' });
  }

  let payload = req.body;
  if (typeof payload === 'string') {
    try { payload = JSON.parse(payload); } catch { return res.status(400).json({ message: 'Invalid request body.' }); }
  }
  if (!payload || typeof payload !== 'object') return res.status(400).json({ message: 'Invalid request body.' });

  // Honeypot: the hidden field is empty for people and filled by many bots.
  if (asText(payload.website, 200)) return res.status(200).json({ ok: true });

  const booking = {
    name: asText(payload.name, 100),
    contact: asText(payload.contact, 300),
    email: asText(payload.email, 254),
    service: asText(payload.service, 120),
    date: asText(payload.date, 500),
    time: asText(payload.time, 1000),
    message: asText(payload.message, 3000),
  };

  if (!booking.name || !booking.contact || !booking.service || !booking.date || !booking.time) {
    return res.status(400).json({ message: 'Please complete all required booking details.' });
  }
  if (booking.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(booking.email)) {
    return res.status(400).json({ message: 'Please provide a valid email address.' });
  }

  try {
    const response = await fetch(GOOGLE_SHEETS_URL, {
      method: 'POST',
      // Apps Script reliably decodes its request body as UTF-8 plain text.
      // This also mirrors the original browser no-cors submission format.
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      body: JSON.stringify(booking),
      redirect: 'follow',
    });
    if (!response.ok) throw new Error(`Google Apps Script responded ${response.status}`);
  } catch (error) {
    console.error('Google Sheets booking write failed:', error);
    return res.status(502).json({ message: 'Unable to save your enquiry right now.' });
  }

  return res.status(200).json({ ok: true });
}
