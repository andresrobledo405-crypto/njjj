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
  const res = await fetch(`${SERVER_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-app-key": APP_KEY },
    body: JSON.stringify({ messages }),
  });
  if (!res.ok) throw new Error(`Servidor: ${res.status}`);
  return (await res.json()).reply;
}
