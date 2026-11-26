import { SERVER_URL, APP_KEY } from "./config";

// history: [{role, content}] ; image: base64 jpeg opcional para el último mensaje
export async function askCloud(history, imageBase64) {
  const messages = history.map((m, i) => {
    const isLast = i === history.length - 1;
    if (isLast && imageBase64 && m.role === "user") {
      return {
        role: "user",
        content: [
          { type: "image", source: { type: "base64", media_type: "image/jpeg", data: imageBase64 } },
          { type: "text", text: m.content || "¿Qué ves en esta imagen?" },
        ],
      };
    }
    return m;
  });
  // Solo los últimos 20 mensajes: acota costo y tamaño; el servidor acepta hasta 40.
  const recent = messages.slice(-20);
  if (recent[0]?.role === "assistant") recent.shift(); // la conversación debe empezar con "user"
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 30000);
  try {
    const res = await fetch(`${SERVER_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-app-key": APP_KEY },
      body: JSON.stringify({ messages: recent }),
      signal: ctl.signal,
    });
    if (res.status === 401) throw new Error("Clave incorrecta: revise APP_KEY en config.js");
    if (res.status === 429) throw new Error("Demasiadas peticiones, espere un minuto");
    if (!res.ok) throw new Error(`Servidor: ${res.status}`);
    return (await res.json()).reply;
  } catch (e) {
    if (e.name === "AbortError") throw new Error("El servidor tardó demasiado en responder");
    if (e instanceof TypeError) throw new Error("No se pudo conectar al servidor. Revise SERVER_URL y la red");
    throw e;
  } finally {
    clearTimeout(timer);
  }
}
