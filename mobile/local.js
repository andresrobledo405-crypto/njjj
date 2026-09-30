// IA 100% en el teléfono con llama.rn (llama.cpp). Requiere build nativo (no funciona en Expo Go):
//   npx expo prebuild && npx expo run:android   (o run:ios)
import * as FileSystem from "expo-file-system";
import { initLlama } from "llama.rn";
import { LOCAL_MODEL_URL } from "./config";

const MODEL_PATH = FileSystem.documentDirectory + "model.gguf";
let ctx = null;

export async function loadLocalModel(onProgress) {
  if (ctx) return;
  const info = await FileSystem.getInfoAsync(MODEL_PATH);
  if (!info.exists) {
    const dl = FileSystem.createDownloadResumable(
      LOCAL_MODEL_URL,
      MODEL_PATH,
      {},
      (p) => onProgress?.(p.totalBytesWritten / p.totalBytesExpectedToWrite)
    );
    await dl.downloadAsync();
  }
  ctx = await initLlama({
    model: MODEL_PATH.replace("file://", ""),
    n_ctx: 2048,
    n_gpu_layers: 0,
  });
}

export async function askLocal(history, onToken) {
  if (!ctx) throw new Error("Modelo local no cargado");
  const messages = [
    { role: "system", content: "Eres un asistente breve y claro. Responde en el idioma del usuario." },
    ...history,
  ];
  const r = await ctx.completion(
    { messages, n_predict: 400, temperature: 0.7, stop: ["<end_of_turn>", "</s>"] },
    (d) => onToken?.(d.token)
  );
  return r.text.trim();
}
