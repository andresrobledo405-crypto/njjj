// URL de su servidor (ver server/) y la misma APP_KEY del .env del servidor.
// En el teléfono NO use localhost: use la IP de su PC (ej. http://192.168.1.20:3000) o su dominio HTTPS.
export const SERVER_URL = "http://192.168.1.20:3000";
export const APP_KEY = "cambie-esto";

// Modelo GGUF pequeño para el modo local (se descarga una sola vez, ~1-2 GB).
export const LOCAL_MODEL_URL =
  "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf";
