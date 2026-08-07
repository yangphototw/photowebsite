const asText = (value, limit) => typeof value === 'string' ? value.trim().slice(0, limit) : '';

const escapeHtml = (value) => value.replace(/[&<>'"]/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
}[char] || char));

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

  const { RESEND_API_KEY: apiKey, BOOKING_FROM_EMAIL: from, BOOKING_RECIPIENT_EMAIL: recipient } = process.env;
  if (!apiKey || !from || !recipient) {
    return res.status(503).json({ message: 'Booking service is not configured yet.' });
  }

  const details = [
    ['Name', booking.name], ['Contact', booking.contact], ['Email', booking.email || '—'],
    ['Service', booking.service], ['Preferred date', booking.date],
    ['Preferred time', booking.time], ['Message', booking.message || '—'],
  ].map(([label, value]) => `<tr><th align="left" style="padding:8px;border:1px solid #ddd">${label}</th><td style="padding:8px;border:1px solid #ddd">${escapeHtml(value)}</td></tr>`).join('');

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from, to: [recipient], reply_to: booking.email || undefined,
      subject: `[Yang Photography] ${booking.service} — ${booking.name}`,
      html: `<h2>New booking enquiry</h2><table style="border-collapse:collapse">${details}</table>`,
    }),
  });

  if (!response.ok) {
    console.error('Resend booking email failed:', response.status);
    return res.status(502).json({ message: 'Unable to send your enquiry right now.' });
  }
  return res.status(200).json({ ok: true });
}
