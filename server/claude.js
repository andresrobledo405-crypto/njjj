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
