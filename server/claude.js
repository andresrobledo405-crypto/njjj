import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic(); // lee ANTHROPIC_API_KEY del entorno
export const MODEL = process.env.CLAUDE_MODEL || "claude-sonnet-5-5";

const SYSTEM =
  "Eres un asistente personal en el teléfono del usuario. Responde en el idioma del usuario, de forma breve y clara.";

// messages: [{ role: "user" | "assistant", content: string | bloques }]
export async function ask(messages, { system = SYSTEM, maxTokens = 1024 } = {}) {
  const res = await client.messages.create({
    model: MODEL,
    max_tokens: maxTokens,
    system,
    messages,
  });
  return res.content
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("");
}

export function streamAsk(messages, opts = {}) {
  return client.messages.stream({
    model: MODEL,
    max_tokens: opts.maxTokens ?? 1024,
    system: opts.system ?? SYSTEM,
    messages,
  });
}

// --- DealFinder: busca ofertas reales con la búsqueda web de Claude ---
const DEALS_SYSTEM = `Eres DealFinder AI, un experto en encontrar las mejores ofertas.
Busca en la web ofertas reales y vigentes del producto pedido. Compara tiendas, descarta precios inflados
(falsos descuentos) y prioriza vendedores confiables. Nunca inventes precios ni enlaces: si no estás seguro, omítelo.
Responde SOLO con un arreglo JSON (sin texto extra, sin markdown) de hasta 6 objetos con esta forma:
{"title": string, "store": string, "price": number|null, "originalPrice": number|null, "currency": string,
 "discountPct": number|null, "url": string, "verdict": string (una frase: por qué sí o no comprar), "score": number (0-100)}
Ordénalos de mejor a peor "score". Si no hay ofertas fiables, responde [].`;

function extractJsonArray(text) {
  const a = text.indexOf("[");
  const b = text.lastIndexOf("]");
  if (a < 0 || b < a) return [];
  try {
    const arr = JSON.parse(text.slice(a, b + 1));
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

const isHttp = (u) => typeof u === "string" && /^https?:\/\//i.test(u);

export async function findDeals(query, { country = "" } = {}) {
  const messages = [
    { role: "user", content: `Producto: ${query}${country ? `\nPaís/mercado: ${country}` : ""}` },
  ];
  let res;
  // La búsqueda web corre en el servidor de Anthropic; si pausa el turno, lo continuamos.
  for (let i = 0; i < 4; i++) {
    res = await client.messages.create({
      model: MODEL,
      max_tokens: 4096,
      system: DEALS_SYSTEM,
      tools: [{ type: "web_search_20250305", name: "web_search", max_uses: 5 }],
      messages,
    });
    if (res.stop_reason !== "pause_turn") break;
    messages.push({ role: "assistant", content: res.content });
  }
  const text = res.content.filter((b) => b.type === "text").map((b) => b.text).join("");
  return extractJsonArray(text)
    .filter((d) => d && d.title && isHttp(d.url)) // descarta enlaces no http(s)
    .map((d) => ({
      title: String(d.title),
      store: String(d.store ?? ""),
      price: Number.isFinite(d.price) ? d.price : null,
      originalPrice: Number.isFinite(d.originalPrice) ? d.originalPrice : null,
      currency: String(d.currency ?? ""),
      discountPct: Number.isFinite(d.discountPct) ? Math.round(d.discountPct) : null,
      url: d.url,
      verdict: String(d.verdict ?? ""),
      score: Number.isFinite(d.score) ? Math.max(0, Math.min(100, Math.round(d.score))) : 0,
    }))
    .sort((x, y) => y.score - x.score);
}
