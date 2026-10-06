import express from "express";
import cors from "cors";
import crypto from "node:crypto";
import { ask, streamAsk, findDeals } from "./claude.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "15mb" })); // fotos en base64
app.use(express.urlencoded({ extended: false })); // webhooks de Twilio

// --- Autenticación simple para la app móvil ---
function requireAppKey(req, res, next) {
  if (!process.env.APP_KEY || req.get("x-app-key") !== process.env.APP_KEY) {
    return res.status(401).json({ error: "No autorizado" });
  }
  next();
}

app.get("/health", (_req, res) => res.json({ ok: true }));

// --- Chat para la app móvil (opción 1) ---
// Body: { messages: [{role, content}] }  content puede incluir imágenes:
// [{type:"image", source:{type:"base64", media_type:"image/jpeg", data:"..."}}, {type:"text", text:"..."}]
app.post("/chat", requireAppKey, async (req, res) => {
  const { messages } = req.body;
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: "messages requerido" });
  }
  try {
    res.json({ reply: await ask(messages) });
  } catch (e) {
    console.error(e);
    res.status(502).json({ error: "Error al consultar a Claude" });
  }
});

// Igual que /chat pero por streaming (Server-Sent Events)
app.post("/chat/stream", requireAppKey, async (req, res) => {
  const { messages } = req.body;
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: "messages requerido" });
  }
  res.set({ "Content-Type": "text/event-stream", "Cache-Control": "no-cache" });
  try {
    const stream = streamAsk(messages);
    stream.on("text", (t) => res.write(`data: ${JSON.stringify({ text: t })}\n\n`));
    await stream.finalMessage();
    res.write("data: [DONE]\n\n");
  } catch (e) {
    console.error(e);
    res.write(`data: ${JSON.stringify({ error: "Error al consultar a Claude" })}\n\n`);
  }
  res.end();
});

// --- DealFinder: busca y compara ofertas ---
// Body: { query: string, country?: string }  ->  { deals: [...] }
app.post("/deals", requireAppKey, async (req, res) => {
  const query = String(req.body.query ?? "").trim().slice(0, 200);
  if (!query) return res.status(400).json({ error: "query requerido" });
  try {
    res.json({ deals: await findDeals(query, { country: String(req.body.country ?? "").slice(0, 60) }) });
  } catch (e) {
    console.error(e);
    res.status(502).json({ error: "Error al buscar ofertas" });
  }
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
const history = new Map();
function remember(key, role, content) {
  const h = history.get(key) ?? [];
  h.push({ role, content });
  history.set(key, h.slice(-20));
  return history.get(key);
}
const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// Webhook "A message comes in" del número de Twilio
app.post("/sms", verifyTwilio, async (req, res) => {
  const from = req.body.From;
  const text = req.body.Body ?? "";
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
app.post("/voice", verifyTwilio, async (req, res) => {
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

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Servidor en http://localhost:${port}`));
