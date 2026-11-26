import express from "express";
import cors from "cors";
import crypto from "node:crypto";
import { ask, streamAsk } from "./claude.js";

const app = express();
app.set("trust proxy", 1); // detrás de Render/Fly/ngrok, req.ip es la IP real
app.use(cors());
app.use(express.json({ limit: "15mb" })); // fotos en base64
app.use(express.urlencoded({ extended: false })); // webhooks de Twilio
// JSON inválido o demasiado grande -> error limpio en vez de stack trace
app.use((err, _req, res, next) => {
  if (!err) return next();
  res.status(err.status || 400).json({ error: err.type === "entity.too.large" ? "Mensaje demasiado grande" : "Petición inválida" });
});

// --- Autenticación simple para la app móvil ---
function safeEqual(a, b) {
  const x = crypto.createHash("sha256").update(String(a)).digest();
  const y = crypto.createHash("sha256").update(String(b)).digest();
  return crypto.timingSafeEqual(x, y);
}
function requireAppKey(req, res, next) {
  const key = process.env.APP_KEY;
  if (!key || !safeEqual(req.get("x-app-key") ?? "", key)) {
    return res.status(401).json({ error: "No autorizado" });
  }
  next();
}

// --- Limitador de peticiones por IP (ventana fija, en memoria, sin dependencias) ---
const RATE_LIMIT = Number(process.env.RATE_LIMIT_PER_MIN) || 30;
const hits = new Map();
setInterval(() => hits.clear(), 60_000).unref();
function rateLimit(req, res, next) {
  const ip = req.ip;
  const n = (hits.get(ip) ?? 0) + 1;
  hits.set(ip, n);
  if (n > RATE_LIMIT) {
    res.set("Retry-After", "60");
    return res.status(429).json({ error: "Demasiadas peticiones, espere un minuto" });
  }
  next();
}

// --- Validación de mensajes: roles válidos, alternancia y tamaño acotado ---
const MAX_MESSAGES = 40;
function validMessages(messages) {
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > MAX_MESSAGES) return false;
  if (messages.some((m) => !m || !["user", "assistant"].includes(m.role) || m.content == null)) return false;
  return messages[messages.length - 1].role === "user";
}

app.get("/health", (_req, res) => res.json({ ok: true }));

// --- Chat para la app móvil (opción 1) ---
// Body: { messages: [{role, content}] }  content puede incluir imágenes:
// [{type:"image", source:{type:"base64", media_type:"image/jpeg", data:"..."}}, {type:"text", text:"..."}]
app.post("/chat", rateLimit, requireAppKey, async (req, res) => {
  const { messages } = req.body ?? {};
  if (!validMessages(messages)) {
    return res.status(400).json({ error: "messages inválido (roles user/assistant, máx. 40, el último de user)" });
  }
  try {
    res.json({ reply: await ask(messages) });
  } catch (e) {
    console.error(e);
    res.status(502).json({ error: "Error al consultar a Claude" });
  }
});

// Igual que /chat pero por streaming (Server-Sent Events)
app.post("/chat/stream", rateLimit, requireAppKey, async (req, res) => {
  const { messages } = req.body ?? {};
  if (!validMessages(messages)) {
    return res.status(400).json({ error: "messages inválido (roles user/assistant, máx. 40, el último de user)" });
  }
  res.set({ "Content-Type": "text/event-stream", "Cache-Control": "no-cache", "X-Accel-Buffering": "no" });
  res.flushHeaders();
  let stream;
  res.on("close", () => stream?.abort()); // el cliente se fue: deja de gastar tokens
  try {
    stream = streamAsk(messages);
    stream.on("text", (t) => res.write(`data: ${JSON.stringify({ text: t })}\n\n`));
    await stream.finalMessage();
    res.write("data: [DONE]\n\n");
  } catch (e) {
    console.error(e);
    res.write(`data: ${JSON.stringify({ error: "Error al consultar a Claude" })}\n\n`);
  }
  res.end();
});

// --- Twilio: SMS y llamadas (opción 4) ---
// Valida la firma X-Twilio-Signature (activa solo si TWILIO_AUTH_TOKEN y PUBLIC_URL están definidos)
function verifyTwilio(req, res, next) {
  const token = process.env.TWILIO_AUTH_TOKEN;
  const base = process.env.PUBLIC_URL;
  if (!token || !base) return next();
  const data = Object.keys(req.body).sort().reduce((a, k) => a + k + req.body[k], base + req.originalUrl);
  const expected = crypto.createHmac("sha1", token).update(data).digest("base64");
  const got = req.get("x-twilio-signature") || "";
  const ok = got.length === expected.length && crypto.timingSafeEqual(Buffer.from(got), Buffer.from(expected));
  return ok ? next() : res.status(403).send("Firma inválida");
}

// Historial por conversación en memoria (use una base de datos en producción).
// Acotado: máx. 500 conversaciones (se descarta la más antigua) y 20 mensajes cada una.
const history = new Map();
const MAX_CONVERSATIONS = 500;
function remember(key, role, content) {
  const h = history.get(key) ?? [];
  h.push({ role, content });
  history.delete(key); // reinsertar = marcar como la más reciente
  history.set(key, h.slice(-20));
  if (history.size > MAX_CONVERSATIONS) history.delete(history.keys().next().value);
  return history.get(key);
}
const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// Webhook "A message comes in" del número de Twilio
app.post("/sms", rateLimit, verifyTwilio, async (req, res) => {
  const from = req.body.From;
  const text = (req.body.Body ?? "").trim();
  if (!text) return res.type("text/xml").send("<Response/>");
  let reply;
  try {
    reply = await ask(remember(`sms:${from}`, "user", text), {
      system: "Respondes por SMS: máximo 300 caracteres, sin formato.",
      maxTokens: 300,
    });
    remember(`sms:${from}`, "assistant", reply);
  } catch (e) {
    console.error(e);
    reply = "Lo siento, hubo un error. Intente de nuevo.";
  }
  res.type("text/xml").send(`<Response><Message>${esc(reply)}</Message></Response>`);
});

// Webhook "A call comes in": conversación por voz con reconocimiento de habla
app.post("/voice", rateLimit, verifyTwilio, async (req, res) => {
  const call = req.body.CallSid;
  const heard = req.body.SpeechResult;
  let say = "Hola, soy su asistente. ¿En qué puedo ayudarle?";
  if (heard) {
    try {
      say = await ask(remember(`call:${call}`, "user", heard), {
        system:
          "Hablas por teléfono: respuestas de una o dos frases, sin listas ni formato.",
        maxTokens: 200,
      });
      remember(`call:${call}`, "assistant", say);
    } catch (e) {
      console.error(e);
      say = "Lo siento, hubo un error.";
    }
  }
  res.type("text/xml").send(
    `<Response><Gather input="speech" language="es-ES" speechTimeout="auto" action="/voice" method="POST">` +
      `<Say language="es-ES">${esc(say)}</Say></Gather>` +
      `<Say language="es-ES">¿Sigue ahí? Adiós.</Say></Response>`
  );
});

// Errores no capturados: respuesta genérica, nunca el stack
app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(500).json({ error: "Error interno" });
});

if (!process.env.ANTHROPIC_API_KEY) console.warn("Aviso: falta ANTHROPIC_API_KEY, /chat fallará.");
if (!process.env.APP_KEY || process.env.APP_KEY === "cambie-esto") console.warn("Aviso: defina una APP_KEY larga y aleatoria.");

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Servidor en http://localhost:${port}`));
